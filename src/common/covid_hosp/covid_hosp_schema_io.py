from datetime import datetime
import pkgutil
import re
import sys
import requests
import json

from delphi.epidata.acquisition.covid_hosp.common.utils import Utils

from delphi.epidata.acquisition.covid_hosp.common.database import Columndef

# ruamel preserves key ordering, comments, and some formatting for a "round trip" of a yaml file import-->export
from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.main import RoundTripRepresenter, round_trip_load as yaml_load, round_trip_dump as yaml_dump

# hacks to print NULLs/nulls as tildes
# inspired by: https://stackoverflow.com/questions/37200150/can-i-dump-blank-instead-of-null-in-yaml-pyyaml
RoundTripRepresenter.represent_none = lambda self, _: self.represent_scalar("tag:yaml.org,2002:null", "~")
RoundTripRepresenter.add_representer(type(None), RoundTripRepresenter.represent_none)
# print(yaml_dump(yaml_load('NULL: ~')))  # ==>  "~: ~\n"

MAX_SQL_NAME_LENGTH = 64
NEWLINE = "\n\t"


def infer_type(col):
    """Guess the type of a new column read from HHS JSON."""
    sqltys = -1
    if col["dataTypeName"] == "text":
        if "cachedContents" not in col:
            raise Exception(f"Can't infer type and/or length without cachedContents:\n{json.dumps(col, indent=2)}")
        if col["cachedContents"]["cardinality"] == "2":
            pyty = "Utils.parse_bool"
            sqlty = "BOOLEAN"
        else:
            pyty = "str"
            max_len = len(col["cachedContents"]["largest"])
            min_len = len(col["cachedContents"]["smallest"])
            if max_len - min_len == 0:
                sqlty = "CHAR"
                sqltys = max_len
            else:
                sqlty = "VARCHAR"
                sqltys = max_len + 5
    if col["dataTypeName"] == "calendar_date":
        pyty = "Utils.int_from_date"
        sqlty = "INT"
    if col["dataTypeName"] == "number":
        if ("cachedContents" in col and col["cachedContents"]["largest"].find(".") < 0) or (
            "cachedContents" not in col and any(col["name"].endswith(x) for x in ["sum", "coverage"])
        ):
            pyty = "int"
            sqlty = "INT"
        else:
            pyty = "float"
            sqlty = "DOUBLE"
    if col["dataTypeName"] == "point":
        pyty = "str"
        sqlty = "VARCHAR"
        sqltys = 32
    if col["dataTypeName"] == "checkbox":
        pyty = "Utils.parse_bool"
        sqlty = "BOOLEAN"
    ret = {"py_type": pyty, "sql_type": sqlty}
    if sqltys > 0:
        ret["sql_type_size"] = sqltys
    return ret


def try_make_shorter(col_name):
    new_name = col_name
    strategies = [
        lambda col_name: col_name.replace("_and_", "_"),
        lambda col_name: col_name.replace("hospitalized", "hosp"),
        lambda col_name: col_name.replace("vaccinated", "vaccd"),
        lambda col_name: col_name.replace("7_day", "7d"),
        lambda col_name: col_name.replace("coverage", "cov"),
    ]
    while len(new_name) > MAX_SQL_NAME_LENGTH:
        if not strategies:
            raise Exception(f"Couldn't shorten '{new_name}' using known strategies")
        strat = strategies.pop(0)
        new_name = strat(new_name)
    return new_name


def get_sql_col_name(col_name):
    new_col_name = col_name
    strategies = [lambda col_name: col_name.replace("-", "_"), lambda col_name: col_name.replace("+", "plus")]
    for strat in strategies:
        new_col_name = strat(new_col_name)
    if len(new_col_name) > MAX_SQL_NAME_LENGTH:
        new_col_name = try_make_shorter(new_col_name)
    return new_col_name.strip()


class CovidHospSomething:
    PYTHON_TYPE_MAPPING = {
        "int": int,
        "float": float,
        "str": str,
        "fixedstr": str,
        "bool": Utils.parse_bool,
        "intdate": Utils.int_from_date,
        "geocode": Utils.limited_geocode,
    }

    SQL_TYPE_MAPPING = {
        "int": "INT",
        "float": "DOUBLE",
        "str": "VARCHAR",
        "fixedstr": "CHAR",
        "bool": "TINYINT(1)",
        "intdate": "INT(11)",
        "geocode": "VARCHAR(32)",
    }

    SOURCE_METADATA_TYPE_MAPPING = {
        "int": "number",
        "float": "number",
        "str": "text",
        "fixedstr": "text",
        "bool": "checkbox/text",
        "intdate": "calendar_date",
        "geocode": "point",
    }

    DS_NAME_METADATA_MAPPING = {
        "covid_hosp_facility": "https://healthdata.gov/api/views/anag-cw7u.json",
        "state_timeseries": "https://healthdata.gov/api/views/g62h-syeh.json",
        "state_daily": "https://healthdata.gov/api/views/6xf2-c3ie.json",
    }

    MYSQL_COL_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,64}$")

    TODAY_STR = datetime.now().strftime("%Y_%m_%d")

    def __init__(self, yaml_file=None, new_yaml_filename=None):
        if yaml_file is None:
            yaml_file = pkgutil.get_data(__name__, "covid_hosp_schemadefs.yaml")

        self.yaml_content = yaml_load(yaml_file, preserve_quotes=True)
        self.new_yaml_file = (
            new_yaml_filename
            if new_yaml_filename is not None
            else f"covid_hosp_schemadefs_{CovidHospSomething.TODAY_STR}.yaml"
        )

    def write_schemadefs(self):
        with open(self.new_yaml_file, "w") as yaml_file:
            # NOTE: `width` specification is to prevent dump from splitting long lines
            # TODO: consider `block_seq_indent=2` to make list under ORDERED_CSV_COLUMNS look a little better
            yaml_dump(self.yaml_content, yaml_file, default_flow_style=False, width=200)

    def dataset(self, ds_name):
        return self.yaml_content[ds_name]

    def dataset_names(self):
        return self.yaml_content.keys()

    def add_column(self, ds_name, col_name, dtype, sql_name=None, col_width=None):
        dtype_cplx = f"{dtype}:{col_width}" if col_width else dtype
        sql_name = sql_name if sql_name else col_name
        if not CovidHospSomething.MYSQL_COL_NAME_PATTERN.match(sql_name):
            raise Exception(f"Invalid name for MySQL column: {sql_name}")

        # TODO: check for name collisions here with self.columns(ds_name)['name', 'sql_name']

        if col_name == sql_name:
            sql_name = None

        # CommentedSeq is a sequence (a list) with formatting for its yaml output
        col = CommentedSeq([dtype_cplx, col_name, sql_name])

        # sets style to "flow", which prints this object in a single line
        col._yaml_format.set_flow_style()

        self.dataset(ds_name)["ORDERED_CSV_COLUMNS"].append(col)

    def columns(self, ds_name):
        for dtype_cplx, name, sql_name in self.dataset(ds_name)["ORDERED_CSV_COLUMNS"]:
            if sql_name is None:
                sql_name = name
            if ":" in dtype_cplx:
                dtype, col_width = dtype_cplx.split(":")
                col_width = int(col_width)
            else:
                dtype = dtype_cplx
                col_width = None
            yield {
                "name": name,
                "sql_name": sql_name,
                "dtype": dtype,
                "col_width": col_width,
                "marshaller": CovidHospSomething.PYTHON_TYPE_MAPPING[dtype],
            }

    def get_aggregate_key_cols(self, ds_name):
        ds = self.dataset(ds_name)
        return ds["AGGREGATE_KEY_COLS"] if "AGGREGATE_KEY_COLS" in ds else None

    def get_ds_info(self, ds_name):
        ds = self.dataset(ds_name)
        TABLE_NAME = ds["TABLE_NAME"]
        KEY_COLS = ds["KEY_COLS"]
        AGGREGATE_KEY_COLS = self.get_aggregate_key_cols(ds_name)
        ORDERED_CSV_COLUMNS = [
            Columndef(
                # Original name for the column
                column["name"],
                # Updated name for the column; same if it's not specified in the YAML files
                column["sql_name"],
                # Datatype for the column, ignoring SQL column length: e.g. fixedstr:1 -> fixedstr -> str
                column["marshaller"],
            )
            for column in self.columns(ds_name)
        ]
        return TABLE_NAME, KEY_COLS, AGGREGATE_KEY_COLS, ORDERED_CSV_COLUMNS

    def get_metadata_info(self, ds_name):
        metadata_info = requests.get(CovidHospSomething.DS_NAME_METADATA_MAPPING[ds_name]).json()
        return metadata_info

    def get_metadata_columns(self, metadata_info):
        metadata_columns = [col for col in metadata_info["columns"] if col.get("computationStrategy") is None]
        metadata_column_names = [col["name"] for col in metadata_columns]
        return metadata_columns, metadata_column_names

    def detect_missing_columns(self, yaml_column_names, metadata_column_names):
        return list(set(metadata_column_names) - set(yaml_column_names))

    def get_missing_columns_metadata(self, missing_columns_names, metadata_columns):
        return list(filter(lambda col: col["name"] in missing_columns_names, metadata_columns))

    def generate_yaml_columns(self, missing_columns):
        new_columns = []
        for column in missing_columns:
            column_info = {"py_name": column["name"], "sql_name": get_sql_col_name(column["name"])}
            try:
                column_types = infer_type(column)
                column_info.update(column_types)
                new_columns.append(column_info)
            except Exception:
                column_info.update({"py_type": None, "sql_type": None})
                new_columns.append(column_info)
        return new_columns

    def detect_changes(self, ds_name):
        ds = self.dataset(ds_name)
        print("TODO download: " + ds["METADATA_ID"])
        metadata_info = self.get_metadata_info(ds_name)
        metadata_columns, metadata_column_names = self.get_metadata_columns(metadata_info)
        yaml_column_names = [col[1] for col in ds["ORDERED_CSV_COLUMNS"]]
        missing_columns_names = self.detect_missing_columns(yaml_column_names, metadata_column_names)
        missing_columns = self.get_missing_columns_metadata(missing_columns_names, metadata_columns)
        new_columns = self.generate_yaml_columns(missing_columns)
        return new_columns

    def generate_create_table_statement(self, ds_name):
        ds = self.dataset(ds_name)
        columns = []
        for column in self.columns(ds_name):
            sql_column_name = column["sql_name"] if column.get("sql_name") else column["name"]
            sql_column_type = CovidHospSomething.SQL_TYPE_MAPPING[column["dtype"]]
            sql_column_width = column.get("column_width")
            if sql_column_width:
                sql_column_type += f"({sql_column_width})"
            not_null = "NOT NULL" if sql_column_name in ds["KEY_COLS"] else ""
            columns.append(f"`{sql_column_name}` {sql_column_type} {not_null}".strip())

        unique_keys = []
        for k, v in ds["UNIQUE_INDEXES"].items():
            cols = ", ".join([f"`{col}`" for col in v])
            unique_keys.append(f"UNIQUE KEY `{k}` ({cols})")

        keys = []
        for k, v in ds["INDEXES"].items():
            cols = ", ".join([f"`{col}`" for col in v])
            keys.append(f"KEY `{k}` ({cols})")

        sql_statement = f"""CREATE TABLE `{ds["TABLE_NAME"]}` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `issue` INT NOT NULL,
        {f",{NEWLINE}".join([column for column in columns])},
        PRIMARY KEY (`id`),
        {f",{NEWLINE}".join([u for u in unique_keys])},
        {f",{NEWLINE}".join([k for k in keys])}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        return sql_statement

    def generate_create_metadata_table_statement(self, ds_name):
        ds = self.dataset(ds_name)
        aggregate_key_cols = self.get_aggregate_key_cols(ds_name)
        if not aggregate_key_cols:
            return
        cols = [column for column in self.columns(ds_name) if column.get("sql_name") in aggregate_key_cols]
        columns = []
        for col in cols:
            sql_column_name = col["sql_name"] if col.get("sql_name") else col["name"]
            sql_column_type = CovidHospSomething.SQL_TYPE_MAPPING[col["dtype"]]
            sql_column_width = col.get("sql_column_width")
            if sql_column_width:
                sql_column_type += f"({sql_column_width})"
            not_null = "NOT NULL" if sql_column_name in ds["KEY_COLS"] else ""
            columns.append(f"`{sql_column_name}` {sql_column_type} {not_null}".strip())

        unique_keys = []
        for k, v in ds["UNIQUE_INDEXES"].items():
            if k not in aggregate_key_cols:
                continue
            cols = ", ".join([f"`{col}`" for col in v])
            unique_keys.append(f"UNIQUE KEY `{k}` ({cols})")

        keys = []
        for k, v in ds["INDEXES"].items():
            if k not in aggregate_key_cols:
                continue
            cols = ", ".join([f"`{col}`" for col in v])
            keys.append(f"KEY `{k}` ({cols})")

        sql_statement = f"""CREATE TABLE `{ds["TABLE_NAME"]}_key` (
        `id` INT NOT NULL AUTO_INCREMENT,
        {f",{NEWLINE}".join([column for column in columns])},
        PRIMARY KEY (`id`),
        {f",{NEWLINE}".join([u for u in unique_keys])},
        {f",{NEWLINE}".join([k for k in keys])}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        return sql_statement

    def get_sql_definition_statement(self, ds_name):
        sql_definition = self.generate_create_table_statement(ds_name)
        nl = "\n\n"
        if self.get_aggregate_key_cols(ds_name):
            sql_definition += f"{nl}{self.generate_create_metadata_table_statement(ds_name)}{nl}"
        return sql_definition

    def generate_migration_statement(self, missing_columns, ds_name):
        migrations = [
            f"`{col['sql_name']}` {col['sql_type'] if col.get('sql_type') is not None else '<Pelase, add type here>'}"
            for col in missing_columns
        ]
        migration_sql_statement = f"""ALTER TABLE {self.dataset(ds_name)['TABLE_NAME']} ADD (
        {f", {NEWLINE}".join([m for m in migrations])}
        )"""
        return migration_sql_statement

    def get_migration_statement(self, new_columns, ds_name):
        sql_migration = self.generate_migration_statement(new_columns, ds_name)
        return sql_migration

    def write_new_definitions(self, sql_definitions, sql_migrations):
        today_str = datetime.now().strftime("%Y_%m_%d")

        ddl_file = "covid_hosp.sql"
        migration_file = f"covid_hosp_v{today_str}.sql"

        # TODO: do these with proper python `pathlib.Path` objects

        # repo_root = "./"
        # yaml_file_dir = repo_root + "src/ddl"
        # ddl_file_dir = repo_root + "src/ddl"
        # migration_file_dir = repo_root + "src/ddl/migrations/"

        # write updated yaml file
        self.write_schemadefs()

        with open(ddl_file, "w") as file:
            file.write(sql_definitions)

        with open(migration_file, "w") as file:
            file.write(sql_migrations)


if __name__ == "__main__":
    chs = CovidHospSomething()
    changed = False
    ddl = ""
    migrations = ""

    for ds_name in chs.yaml_content:
        ds = chs.dataset(ds_name)
        new_cols = chs.detect_changes(ds_name)
        if new_cols:
            changed = True
            for col in new_cols:
                chs.add_column(ds_name, col.get("py_name"), col.get("py_type"), col.get("sql_name"))
            migrations += chs.get_migration_statement(new_cols, ds_name)
        ddl += chs.get_sql_definition_statement(ds_name)
    if changed:
        print("column changes detected, writing new definition files")
        chs.write_new_definitions(ddl, migrations)
        sys.exit(1)

    print("no changes detected, exiting")
    sys.exit(0)
