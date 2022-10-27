import json
import requests
import csv
from dataclasses import dataclass
import importlib.util
import sys

import itertools
from collections import defaultdict
from typing import Callable
from mo_sql_parsing import parse_mysql

from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database as STDatabase
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database as SDDatabase
from delphi.epidata.acquisition.covid_hosp.facility.database import Database as FDatabase

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
    result = defaultdict(list)
    for stmt in split_sql(sql):
        if stmt[:15].lower().startswith("create table"):
            ast = parse_mysql(sql)['create table']
            if ast['name'] not in all_columns:
                continue
            for pydb_columns in all_columns[ast['name']]:
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
                result[ast['name']].append(remapped)
    return result

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
        parts.append(self.sql_name)
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

#    state: "https://healthdata.gov/api/views/g62h-syeh.json"
# facility: "https://healthdata.gov/api/views/anag-cw7u.json"

def main():
    all_columns = {
        "covid_hosp_state_timeseries": [
            db_to_columns(STDatabase),
            db_to_columns(SDDatabase)
        ],
        "covid_hosp_facility": [
            db_to_columns(FDatabase)
        ]
    }
