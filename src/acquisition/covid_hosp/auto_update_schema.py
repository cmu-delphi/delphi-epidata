import json
import requests
import csv
from dataclasses import dataclass
import importlib.util
import sys
import re

import itertools
from collections import defaultdict
from typing import Callable
from mo_sql_parsing import parse_mysql
from mo_parsing.exceptions import ParseException

from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database as STDatabase
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database as SDDatabase
from delphi.epidata.acquisition.covid_hosp.facility.database import Database as FDatabase

MAX_SQL_NAME_LENGTH = 64

#    state: "https://healthdata.gov/api/views/g62h-syeh.json"
# facility: "https://healthdata.gov/api/views/anag-cw7u.json"

def db_to_columns(db_impl):
    """Convert database.py:Database implementation to a set of Column representations."""
    columns = {}
    for (csv_name, sql_name, initializer) in db_impl.ORDERED_CSV_COLUMNS:
        columns[csv_name] = Column(
            csv_name=csv_name,
            sql_name=sql_name,
            py_type=initializer
        )
    return columns

def split_sql(sql):
    """Split a .sql DDL file string into single-statement blocks for mo_sql_parsing."""
    def recur(text, delim):
        if not text:
            return []
        pre, d, post = text.partition(delim)
        pre = pre.strip()
        if not pre:
            return recur(post.strip(), delim)
        return [pre] + recur(post.strip(), delim)
    cursor = [sql]
    for delim in [";", "/*", "*/"]:
        result = [recur(s, delim) for s in cursor]
        cursor = list(itertools.chain(*result))
    return cursor

def annotate_columns_using_ddl(all_columns, sql):
    """Parse a .sql DDL file string and annotate a set of Column representations with SQL type and index information."""
    result = defaultdict(dict)
    for stmt in split_sql(sql):
        if stmt[:15].lower().startswith("create table"):
            try:
                ast = parse_mysql(stmt)['create table']
            except ParseException:
                print(
                    "\n".join(f"{i} {x}" for i,x in enumerate(stmt.split("\n"))),
                    file=sys.stderr
                )
                raise
            if ast['name'] not in all_columns:
                continue
            for pydb_module in all_columns[ast['name']]:
                pydb_columns = all_columns[ast['name']][pydb_module]
                remapped = {
                    ci.sql_name: ci
                    for ci in pydb_columns.values()
                }
                for ci in ast['columns']:
                    if ci['name'] not in remapped:
                        remapped[ci['name']] = Column()
                    remapped[ci['name']].update_from_sql(ci)
                if 'constraint' in ast:
                    for ci in ast['constraint']:
                        if 'primary_key' in ci:
                            pks = ci['primary_key']['columns']
                            if isinstance(pks, str):
                                pks = [pks]
                            for pki in pks:
                                remapped[pki].sql_key = "pri"
                        if 'index' in ci and 'unique' in ci['index'] and ci['index']['unique']:
                            mks = ci['index']['columns']
                            for mki in mks:
                                remapped[mki].sql_key = "mul"
                result[ast['name']][pydb_module] = remapped
    return result

def url_as_json_data(json_url):
    resp = requests.get(json_url)
    resp.raise_for_status()
    return resp.json()['columns']

KEYS="name fieldName position description dataTypeName cachedContents".split()
TABLE_HEADERS = "Field Type Null Key Default Extra".split()
HEADER = {
    "publication_date",
    "address",
    "ccn",
    "city",
    "collection_week",
    "fips_code",
    "geocoded_hospital_address",
    "hhs_ids",
    "hospital_name",
    "hospital_pk",
    "hospital_subtype",
    "is_metro_micro",
    "state",
    "zip",
    "issue",
    "date"
}
REQUIRED = {
    "publication_date",
    "collection_week",
    "hospital_pk",
    "state",
    "issue",
    "date"
}
RE_NUMBERED_PREFIX = re.compile(r'^[0-9]*\.')
#RE_THIRD=re.compile(",[^,]*,$")
#RE_NAME=re.compile("`[^`]*`")
#RE_REQUIRED=re.compile(" NOT NULL")
#RE_TYPE=re.compile("^([A-Z]*)(\([0-9]*\))*")

def infer_type(col):
    """Guess the type of a new column read from HHS JSON."""
    sqltys = -1
    if col['dataTypeName'] == 'text':
        if col['cachedContents']['cardinality'] == "2":
            pyty = "Utils.parse_bool"
            sqlty = "BOOLEAN"
        else:
            pyty = "str"
            max_len = len(col['cachedContents']['largest'])
            min_len = len(col['cachedContents']['smallest'])
            if max_len - min_len == 0:
                sqlty = "CHAR"
                sqltys = max_len
            else:
                sqlty = "VARCHAR"
                sqltys = max_len+5
    if col['dataTypeName'] == 'calendar_date':
        pyty = "Utils.int_from_date"
        sqlty = "INT"
    if col['dataTypeName'] == 'number':
        if col['cachedContents']['largest'].find('.') < 0:
            pyty = "int"
            sqlty = "INT"
        else:
            pyty = "float"
            sqlty = "DOUBLE"
    if col['dataTypeName'] == 'point':
        pyty = "str"
        sqlty = "VARCHAR"
        sqltys = 32
    if col['dataTypeName'] == 'checkbox':
        pyty = "Utils.parse_bool"
        sqlty = "BOOLEAN"
    ret = {
        "py_type": pyty,
        "sql_type": sqlty
    }
    if sqltys > 0:
        ret["sql_type_size"] = sqltys
    return ret

def trie_dict_safe_insert(trie_dict, name):
    segmented_name = name.split("_")
    if segmented_name[0] not in trie_dict:
        trie_dict[segmented_name[0]] = TrieNode(segmented_name[0])
    return trie_dict[segmented_name[0]].insert(segmented_name[1:])


def extend_columns_with_current_json(columns, json_data):
    """Add new columns found in json_data to existing set of columns read from python/SQL files."""
    hits = []
    misses = []
    new_names = {}
    for json_column in json_data:
        if 'computationStrategy' in json_column:
            continue
        if not all(key in json_column for key in KEYS):
            print(f"Bad column: {json.dumps(json_column, indent=2)}")
            continue
        if json_column['name'] in columns:
            hits.append(json_column['name'])
        else:
            new_column = Column(
                csv_name=json_column['name'],
                csv_order=json_column['position'],
                desc=re.sub(RE_NUMBERED_PREFIX, "", json_column['description']).strip(),
                sql_name=json_column['fieldName'].lower(),
                **infer_type(json_column)
            )
            misses.append(new_column)
            columns[new_column.csv_name] = new_column
            new_column.trie = trie_dict_safe_insert(new_names, new_column.sql_name)
    n_oversize = 0
    for miss in misses:
        TrieNode.try_make_shorter(miss.trie)
    for miss in misses:
        miss.sql_name = miss.trie.as_shortened_name()
        if len(miss.sql_name) > MAX_SQL_NAME_LENGTH:
            n_oversize += 1
            print(
                "Oversize column name:\n{miss.csv_name}\n{miss.sql_name}\n{len(miss_sql_name)}",
                file=sys.stderr
            )
    if n_oversize > 0:
        raise Exception("Oversize column names found; add another name-shortening strategy")
    return hits, misses

TRIE_END = object()
class TrieNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.short_name = name
        self.children = dict()
        self.parent = parent
    def insert(self, words):
        if not words:
            self.children.setdefault(TRIE_END, TRIE_END)
            return self
        return self.children.setdefault(words[0], TrieNode(words[0], self)).insert(words[1:])
    def set_short_name(self, new_name):
        self.short_name = new_name
        return True # permit chaining with `and`
    def as_shortened_name(self, end=None):
        if end is None: end = list()
        if self.short_name:
            end.insert(0, self.short_name)
        if self.parent is None:
            return "_".join(end)
        return self.parent.as_shortened_name(end)
    def longest(self, longest=(0, None)):
        if len(self.short_name) > longest[0]:
            longest = (len(self.short_name), self)
        if parent:
            return parent.longest(longest)
        else:
            return longest[-1]
    @classmethod
    def try_make_shorter(self, trie):
        strategies = [
            (lambda c: c.short_name == "and",
             lambda c: c.set_short_name("")),
            (lambda c: c.short_name == "hospitalized",
             lambda c: c.set_short_name("hosp")),
            (lambda c: c.short_name == "vaccinated",
             lambda c: c.set_short_name("vaccd")),
            (lambda c: (
                c.short_name == "7" and
                "day" in c.children and
                len(c.children) == 1
            ),
             lambda c: (
                 c.set_short_name("7d") and
                 c.children["day"].set_short_name("")
             )),
            (lambda c: c.short_name == "coverage",
             lambda c: c.set_short_name("cov"))
        ]
        while len(trie.as_shortened_name()) > MAX_SQL_NAME_LENGTH:
            if not strategies:
                raise Exception(f"Couldn't shorten '{trie.as_shortened_name()}' using known strategies")
            strat = strategies.pop(0)
            cursor = trie
            while cursor and not strat[0](cursor):
                cursor = cursor.parent
            if cursor:
                strat[1](cursor)

def create_migration(table, misses, migrations_file):
    migrations_file.write(f"ALTER TABLE {table} ADD COLUMN (\n")
    migrations_file.write(",\n".join(
        miss.render_sql() for miss in misses
    ))
    migrations_file.write("\n);")
        
@dataclass
class Column:
    """Store column information ready to output in either Python database.py or DDL .sql format."""
    csv_name: str = ""
    desc: str = ""
    csv_order: int = -1
    sql_name: str = ""
    sql_type: str = ""
    sql_type_size: str = ""
    sql_key: str = ""
    sql_extra: str = ""
    py_type: Callable[[str], object] = None
    header: bool = False
    required: bool = False

    def update_from_sql(self, ast_column):
        # examples of mo_sql_parsing column output:
        # {'name': 'id', 'type': {'int': {}}, 'nullable': False, 'auto_increment': True}
        # {'name': 'hospital_pk', 'type': {'varchar': 128}, 'nullable': False}
        if 'type' in ast_column:
            for t in ast_column['type']:
                self.sql_type = t
                if isinstance(ast_column['type'][t], int):
                    self.sql_type_size = ast_column['type'][t]
        if 'nullable' in ast_column:
            self.required = not ast_column['nullable']

    def set_full_sql_type(self):
        self.full_sql_type = self.sql_type
        if self.sql_type_size:
            self.full_sql_type += f"({self.sql_type_size})"

    def render_sql(self):
        if not hasattr(self, "full_sql_type"):
            self.set_full_sql_type()
        parts = []
        parts.append(f"`{self.sql_name}`")
        parts.append(self.full_sql_type.upper())
        parts.append('NOT NULL' if self.required else '')
        parts.append(self.sql_extra.upper())
        return " ".join(parts).strip()
    
    def as_table_list(self):
        if not hasattr(self, "full_sql_type"):
            self.set_full_sql_type()
        return [
            self.sql_name,
            self.full_sql_type.lower(),
            "NO" if self.required else "YES",
            self.sql_key.upper(),
            "NULL",
            self.sql_extra.upper()
        ]


#    state ts: "https://healthdata.gov/api/views/g62h-syeh.json"
# state daily: "https://healthdata.gov/api/views/6xf2-c3ie.json"
#    facility: "https://healthdata.gov/api/views/anag-cw7u.json"

def main(path_to_epidata):
    all_columns = {
        "covid_hosp_state_timeseries": {
            "state_timeseries": db_to_columns(STDatabase),
            "state_daily": db_to_columns(SDDatabase)
        },
        "covid_hosp_facility": {
            "facility": db_to_columns(FDatabase)
        }
    }
    with open(f"{path_to_epidata}/src/ddl/covid_hosp.sql") as f:
        ddl = f.read()
    annotate_columns_using_ddl(all_columns, ddl)
    hits, misses = extend_columns_with_current_json(
        all_columns["covid_hosp_state_timeseries"]["state_timeseries"],
        url_as_json_data("https://healthdata.gov/api/views/g62h-syeh.json")
    )
    return (hits, misses, all_columns)

if __name__=='__main__':
    import sys
    if len(sys.argv)<1:
        print(f"Usage: {sys.argv[0]} path/to/delphi-epidata")
        exit(0)
    (hits, misses, all_columns) = main(sys.argv[-1])
