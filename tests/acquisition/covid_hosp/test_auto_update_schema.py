from collections import namedtuple
from dataclasses import dataclass
from io import StringIO
from unittest.mock import patch
from delphi.epidata.acquisition.covid_hosp.auto_update_schema import \
    split_sql, \
    db_to_columns, \
    annotate_columns_using_ddl, \
    extend_columns_with_current_json, \
    infer_type, \
    TrieNode, TRIE_END, \
    Column, \
    create_migration
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
import pytest

Case = namedtuple("testcase","name given expected")

@pytest.fixture
def split_sql_example():
    return Case(
        "split_sql",
        """
USE covidcast;
/*
xyzzy
*/

CREATE TABLE `kitchen` (
`id` INT NOT NULL AUTO_INCREMENT,
sink VARCHAR(8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
quux
| bar |
*/

CREATE TABLE `maze` (
`turn` INT NOT NULL AUTO_INCREMENT,
`direction` CHAR(2) NOT NULL,
-- test comment
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `corners` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `issue` INT NOT NULL,
  `state` CHAR(2) NOT NULL,
  `date` INT NOT NULL,
  `record_type` CHAR(1) NOT NULL,
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of most recent issue for a given state, date, and record type
  UNIQUE KEY `issue_by_state_and_date` (`state`, `date`, `issue`, `record_type`),
  -- for fast lookup of a time-series for a given state, issue, and record type
  KEY `date_by_issue_and_state` (`issue`, `state`, `date`, `record_type`),
  -- for fast lookup of all states for a given date, issue, and record_type
  KEY `state_by_issue_and_date` (`issue`, `date`, `state`, `record_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
""",
        # x[1:] to drop the initial newline (included for readability)
        list(x[1:] for x in [
            """
USE covidcast""",
            """
xyzzy""",
            """
CREATE TABLE `kitchen` (
`id` INT NOT NULL AUTO_INCREMENT,
sink VARCHAR(8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8""",
            """
quux
| bar |""",
            """
CREATE TABLE `maze` (
`turn` INT NOT NULL AUTO_INCREMENT,
`direction` CHAR(2) NOT NULL,
-- test comment
) ENGINE=InnoDB DEFAULT CHARSET=utf8""",
            """
CREATE TABLE `corners` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `issue` INT NOT NULL,
  `state` CHAR(2) NOT NULL,
  `date` INT NOT NULL,
  `record_type` CHAR(1) NOT NULL,
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of most recent issue for a given state, date, and record type
  UNIQUE KEY `issue_by_state_and_date` (`state`, `date`, `issue`, `record_type`),
  -- for fast lookup of a time-series for a given state, issue, and record type
  KEY `date_by_issue_and_state` (`issue`, `state`, `date`, `record_type`),
  -- for fast lookup of all states for a given date, issue, and record_type
  KEY `state_by_issue_and_date` (`issue`, `date`, `state`, `record_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8"""
        ]))


def test_split_sql(split_sql_example):
    assert split_sql(split_sql_example.given) == split_sql_example.expected

@pytest.fixture
def columns_as_Database():
    class Database:
        ORDERED_CSV_COLUMNS = [
            ("int_csv", "int_sql", int),
            ("str_csv", "str_sql", str),
            ("float_csv", "float_sql", float),
            ("date_csv", "date_sql", Utils.int_from_date)
        ]
    return Database

@pytest.fixture
def columns_as_Columns():
    initializers = [int, str, float, Utils.int_from_date]
    return {
        f"{t}_csv": Column(
            csv_name=f"{t}_csv",
            sql_name=f"{t}_sql",
            py_type=initializers[i]
        ) for i, t in enumerate(["int", "str", "float", "date"])
    }


def _match_fields(actual, expected, *fields):
    for fi in fields:
        assert getattr(actual, fi) == getattr(expected, fi)


def test_db_to_columns(columns_as_Database, columns_as_Columns):
    actual = db_to_columns(columns_as_Database)
    for ki in set(list(actual) + list(columns_as_Columns)):
        assert ki in actual
        assert ki in columns_as_Columns
        _match_fields(
            actual[ki],
            columns_as_Columns[ki],
            *"csv_name sql_name py_type".split()
        )

@pytest.fixture
def columns_as_SQL():
    return """
CREATE TABLE `table1` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `int_sql` INT NOT NULL,
  `str_sql` VARCHAR(8) NOT NULL,
  `float_sql` DOUBLE,
  `date_sql` INT(8) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `str_by_date` (`str_sql`, `date_sql`),
  KEY `date_by_str` (`date_sql`, `str_sql`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

@pytest.fixture
def annotated_columns(columns_as_Columns):
    def update(c, sql_type, sql_type_size=None, required=False, extra=None):
        c.sql_type = sql_type
        if sql_type_size is not None:
            c.sql_type_size = sql_type_size
        c.required = required
        if extra:
            c.sql_extra = extra
    update(columns_as_Columns['int_csv'], "int", required=True)
    update(columns_as_Columns['str_csv'], "varchar", 8, True)
    update(columns_as_Columns['float_csv'], "double")
    update(columns_as_Columns['date_csv'], "int", 8, True)
    return columns_as_Columns

def test_annotate_columns_using_ddl(columns_as_Columns, columns_as_SQL, annotated_columns):
    remapped = annotate_columns_using_ddl(
        {'table1': {'module1': columns_as_Columns}},
        columns_as_SQL
    )
    assert 'id' not in annotated_columns
    assert 'id' in remapped['table1']['module1']
    for ki in annotated_columns:
        _match_fields(
            columns_as_Columns[ki],
            annotated_columns[ki],
            *"sql_type sql_type_size required".split()
        )

@pytest.fixture(
    params=["{i}. Description of {name}", "Description of {name}"],
    ids=["numbered descriptions", "non-numbered descriptions"]
)
def old_columns_as_JSON(request):
    columns = [
        ("int", "number"),
        ("str", "text"),
        ("float", "number"),
        ("date", "calendar_date"),
    ]
    return [
        {
            "id": 100 + i,
            "name": f"{name}_csv",
            "dataTypeName": dataTypeName,
            "description": request.param.format(i=i, name=name),
            "fieldName": f"{name}_csv",
            "position": i,
            "cachedContents": [],
        }
        for i, (name, dataTypeName) in enumerate(columns)
    ]


@dataclass
class Case_new_column:
    name: str
    given: dict
    expected_type: dict
    expected_column: Column=None

json_columns = [
    Case_new_column(
        "text_bool", # literal "true" / "false" strings
        {
            "dataTypeName": "text",
            "cachedContents": {
                "cardinality": "2",
                
            }
        },
        {
            "py_type": "Utils.parse_bool",
            "sql_type": "BOOLEAN"
        }
    ),
    Case_new_column(
        "text_same_length",
        {
            "dataTypeName": "text",
            "cachedContents": {
                "cardinality": 0,
                "largest": "x",
                "smallest": "x"
            }
        },
        {
            "py_type": "str",
            "sql_type": "CHAR",
            "sql_type_size": 1
        }
    ),
    Case_new_column(
        "text_different_lengths",
        {
            "dataTypeName": "text",
            "cachedContents": {
                "cardinality": 0,
                "largest": "xx",
                "smallest": "x",
            }
        },
        {
            "py_type": "str",
            "sql_type": "VARCHAR",
            "sql_type_size": 7
        }
    ),
    Case_new_column(
        "dates",
        {
            "dataTypeName": "calendar_date",
        },
        {
            "py_type": "Utils.int_from_date",
            "sql_type": "INT",
        }
    ),
    Case_new_column(
        "ints", # number: integer
        {
            "dataTypeName": "number",
            "cachedContents": {
                "largest": "0"
            }
        },
        {
            "py_type": "int",
            "sql_type": "INT",
        }
    ),
    Case_new_column(
        "floats", # number: float
        {
            "dataTypeName": "number",
            "cachedContents": {
                "largest": "0.0"
            }
        },
        {
            "py_type": "float",
                "sql_type": "DOUBLE",
        }
    ),
    Case_new_column(
        "points", # lat/long point
        {
            "dataTypeName": "point",
        },
        {
            "py_type": "str",
            "sql_type": "VARCHAR",
            "sql_type_size": 32
        }
    ),
    Case_new_column(
        "checkboxes",
        {
            "dataTypeName": "checkbox",
        },
        {
            "py_type": "Utils.parse_bool",
            "sql_type": "BOOLEAN",
        }
    )
]

@pytest.fixture(
    params=json_columns,
    ids=[j.name for j in json_columns]
)
def new_columns(request):
    return Case_new_column(
        request.param.name,
        {
            "id": 500,
            "name": f"xyzzy_csv",
            "dataTypeName": request.param.given["dataTypeName"],
            "description": "Description of xyzzy",
            "fieldName": f"xyzzy_csv",
            "position": 10,
            "cachedContents": request.param.given.get("cachedContents", {}),
        },
        request.param.expected_type,
        Column(
            csv_name="xyzzy_csv",
            csv_order=10,
            desc="Description of xyzzy",
            sql_name="xyzzy_csv",
            **request.param.expected_type
        ),
    )

@pytest.fixture()
def new_ignore_column():
    return Case(
        "ignore this column",
        {
            "computationStrategy": {}
        },
        []
    )

def test_infer_type(new_columns):
    assert infer_type(new_columns.given) == new_columns.expected_type    

def test_extend_columns_with_current_json(columns_as_Columns, old_columns_as_JSON, new_columns):
    hits, misses = extend_columns_with_current_json(
        columns_as_Columns,
        old_columns_as_JSON + [new_columns.given]
    )
    assert hits == [
        "int_csv",
        "str_csv",
        "float_csv",
        "date_csv"
    ]
    assert misses == [new_columns.expected_column]

def test_extend_columns_ignore_column(columns_as_Columns, new_ignore_column):
    hits, misses = extend_columns_with_current_json(
        columns_as_Columns,
        [new_ignore_column.given]
    )
    assert misses == new_ignore_column.expected

@pytest.fixture
def empty_trie():
    return TrieNode("empty")

def test_trie_insert(empty_trie):
    empty_trie.insert([])
    assert TRIE_END in empty_trie.children
    empty_trie.insert(["x"])
    assert "x" in empty_trie.children
    assert isinstance(empty_trie.children["x"], TrieNode)
    assert empty_trie.children["x"].name == "x"
    assert empty_trie.children["x"].parent == empty_trie

def test_trie_as_shortened_name(empty_trie):
    assert empty_trie.as_shortened_name() == "empty"
    x = empty_trie.insert("x")
    assert x.as_shortened_name() == "empty_x"
    empty_trie.short_name = "e"
    assert x.as_shortened_name() == "e_x"


LONG_ELEMENTS = [
    Case('hospitalized',
         'hospitalized',
         'hosp'),
    Case('vaccinated',
         'vaccinated',
         'vaccd'),
    Case('coverage',
         'coverage',
         'cov')
]        
@pytest.fixture(
    params=LONG_ELEMENTS,
    ids=[el.name for el in LONG_ELEMENTS]
)
def long_name_elements(request):
    return request.param

@patch('delphi.epidata.acquisition.covid_hosp.auto_update_schema.MAX_SQL_NAME_LENGTH', 5)
def test_trie_make_shorter(long_name_elements):
    trie = TrieNode(long_name_elements.given)
    TrieNode.try_make_shorter(trie)
    assert trie.short_name == long_name_elements.expected

LONG_COLUMN_NAMES = [
    Case('hosp_and_no_cov',
         'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_coverage',
         'total_pediatric_patients_hosp_confirmed_suspected_covid_coverage'),
    Case('vaccd_no7d',
         'previous_week_personnel_covid_vaccinated_doses_administered_7_day_sum',
         'previous_week_personnel_covid_vaccd_doses_administered_7_day_sum',),
    Case('and_7d_nocov',
         'staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_coverage',
         'staffed_icu_adult_patients_confirmed_suspected_covid_7d_coverage'),
    Case('hosp_and_7d_nocov',
         'total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage',
         'total_adult_patients_hosp_confirmed_suspected_covid_7d_coverage')
]
@pytest.fixture(
    params=LONG_COLUMN_NAMES,
    ids=[el.name for el in LONG_COLUMN_NAMES]
)
def long_column_names(request):
    return Case(
        request.param.name,
        request.param.given.split("_"),
        request.param.expected
    )

def test_trie_make_all_shorter(long_column_names):
    trie = TrieNode(long_column_names.given[0]).insert(long_column_names.given[1:])
    TrieNode.try_make_shorter(trie)
    assert trie.as_shortened_name() == long_column_names.expected


@pytest.fixture
def oversize_new_columns():
    oversize_name = "x" * 65
    return Case(
        "oversize new column",
        {
            "id": 500,
            "name": oversize_name,
            "dataTypeName": "number",
            "description": "Description of oversize column",
            "fieldName": oversize_name,
            "position": 10,
            "cachedContents": {
                "largest": "0"
            }
        },
        Exception
    )

def test_extend_columns_with_current_json_oversize_column(columns_as_Columns, oversize_new_columns):
    with pytest.raises(Exception):
        hits, misses = extend_columns_with_current_json(
            columns_as_Columns,
            [oversize_new_columns.given]
        )

SQL_COLUMNS = [
    Case("int",
         Column(sql_name="x_int", sql_type="INT"),
         "`x_int` INT"
    ),
    Case("int required auto increment",
         Column(sql_name="x_auto", sql_type="INT", required=True, sql_extra="AUTO_INCREMENT"),
         "`x_auto` INT NOT NULL AUTO_INCREMENT"
    ),
    Case("varchar",
         Column(sql_name="x_varchar", sql_type="VARCHAR", sql_type_size="1"),
         "`x_varchar` VARCHAR(1)"
    ),
    Case("varchar required",
         Column(sql_name="x_varchar_required", sql_type="VARCHAR", sql_type_size="1", required=True),
         "`x_varchar_required` VARCHAR(1) NOT NULL"
    ),
]
@pytest.fixture(params=SQL_COLUMNS)
def sql_column(request):
    yield request.param

def test_column_render_sql(sql_column):
    assert sql_column.given.render_sql() == sql_column.expected

@pytest.fixture
def column_misses():
    return Case(
        "misses",
        ["xyzzy", [case.given for case in SQL_COLUMNS]],
        "\n".join([
            "ALTER TABLE xyzzy ADD COLUMN (",
            ",\n".join(case.expected for case in SQL_COLUMNS),
            ");"
        ])
    )

def test_create_migration(column_misses):
    mock_migrations_file = StringIO()
    create_migration(*column_misses.given, mock_migrations_file)
    assert mock_migrations_file.getvalue() == column_misses.expected
