from collections import namedtuple
from datetime import datetime
from pathlib import Path
import re
import sys

from delphi.epidata.acquisition.covid_hosp.common.utils import Utils

# ruamel preserves key ordering, comments, and some formatting for a "round trip" of a yaml file import-->export
from ruamel.yaml.main import (
  RoundTripRepresenter,
  round_trip_load as yaml_load,
  round_trip_dump as yaml_dump)

# hacks to print NULLs/nulls as tildes
# inspired by: https://stackoverflow.com/questions/37200150/can-i-dump-blank-instead-of-null-in-yaml-pyyaml
RoundTripRepresenter.represent_none = lambda self,_ : self.represent_scalar('tag:yaml.org,2002:null', "~")
RoundTripRepresenter.add_representer(type(None), RoundTripRepresenter.represent_none)
# print(yaml_dump(yaml_load('NULL: ~')))  # ==>  "~: ~\n"


Columndef = namedtuple("Columndef", "csv_name sql_name dtype")

class CovidHospSomething:

  PYTHON_TYPE_MAPPING = {
    'int': int,
    'float': float,
    'str': str,
    'fixedstr': str,
    'bool': Utils.parse_bool,
    'intdate': Utils.int_from_date,
    'geocode': Utils.limited_geocode,
  }

  SQL_TYPE_MAPPING = {
    'int': 'INT',
    'float': 'DOUBLE',
    'str': 'VARCHAR',
    'fixedstr': 'CHAR',
    'bool': 'TINYINT(1)',
    'intdate': 'INT(11)',
    'geocode': 'VARCHAR(32)',
  }

  SOURCE_METADATA_TYPE_MAPPING = {
    'int': 'number',
    'float': 'number',
    'str': 'text',
    'fixedstr': 'text',
    'bool': 'checkbox/text',
    'intdate': 'calendar_date',
    'geocode': 'point',
  }

  MYSQL_COL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,64}$')


  def __init__(self, yaml_filename=None):
    if not yaml_filename:
      # the default schema definitions yaml file is a member of the current package
      # TODO: use `importlib_resources` instead of generic file Path stuff to load this, once we are past python 3.8
      yaml_filename = str(Path(__file__).parent.absolute()) + "/covid_hosp_schemadefs.yaml"
    self.yaml_filename = yaml_filename

    with open(yaml_filename, 'r') as yaml_file:
      self.yaml_content = yaml_load(yaml_file, preserve_quotes=True)


  def write_schemadefs(self, yaml_filename=None):
    if not yaml_filename:
      yaml_filename = self.yaml_filename

    with open(yaml_filename, 'w') as yaml_file:
      # NOTE: `width` specification is to prevent dump from splitting long lines
      # TODO: consider `block_seq_indent=2` to make list under ORDERED_CSV_COLUMNS look a little better
      yaml_dump(self.yaml_content, yaml_file, width=200)


  def dataset_names(self):
    return self.yaml_content.keys()


  def dataset(self, ds_name):
    return self.yaml_content[ds_name]


  def columns(self, ds_name):
    for dtype_cplx, name, sql_name in self.dataset(ds_name)['ORDERED_CSV_COLUMNS']:
      if sql_name is None:
        sql_name = name
      if ':' in dtype_cplx:
        dtype, col_width = dtype_cplx.split(':')
        col_width = int(col_width)
      else:
        dtype = dtype_cplx
        col_width = None
      yield {'name': name, 'sql_name': sql_name, 'dtype': dtype, 'col_width': col_width, 'marshaller': CovidHospSomething.PYTHON_TYPE_MAPPING[dtype]}


  def add_column(self, ds_name, col_name, dtype, sql_name=None, col_width=None):
    # if provided, append a column width to the type
    if col_width:
      dtype_cplx = f"{dtype}:{col_width}"
    else:
      dtype_cplx = dtype

    # verify name to be used for MySQL column is acceptable
    if sql_name is None:
      sql_name = col_name
    if not CovidHospSomething.MYSQL_COL_NAME_PATTERN.match(sql_name):
      raise Exception(f"Invalid name for MySQL column: {sql_name}")

    # TODO: check for name collisions here with self.columns(ds_name)['name', 'sql_name']

    # for readability of resulting YAML output, dont repeat SQL column name when it matches original
    if col_name == sql_name:
      sql_name = None

    # add new column to end of current column list
    self.dataset(ds_name)['ORDERED_CSV_COLUMNS'].append([dtype_cplx, col_name, sql_name])


  def get_ds_table_name(self, ds_name):
    return self.dataset(ds_name)['TABLE_NAME']


  def get_ds_key_cols(self, ds_name):
    return self.dataset(ds_name)['KEY_COLS']


  def get_ds_aggregate_key_cols(self, ds_name):
    return self.dataset(ds_name).get('AGGREGATE_KEY_COLS', [])


  def get_ds_dataset_id(self, ds_name):
    return self.dataset(ds_name)['DATASET_ID']


  def get_ds_metadata_id(self, ds_name):
    return self.dataset(ds_name)['METADATA_ID']


  def get_ds_issue_column(self, ds_name):
    return self.dataset(ds_name).get('ISSUE_COLUMN', 'issue')


  def get_ds_ordered_csv_cols(self, ds_name):
    return [
      Columndef(
        # Original name for the column
        column['name'],
        # Updated name for the column; same name if it's not specified in the YAML files
        column['sql_name'],
        # Datatype for the column, ignoring SQL column lengths: e.g. fixedstr:1 -> fixedstr -> str
        column['marshaller']
      )
      for column in self.columns(ds_name)
    ]


  def detect_changes(self, ds_name):
    # TODO
    ds = self.dataset(ds_name)
    print("TODO download: " + ds['METADATA_ID'])
    # TODO: compute set difference: metadata.columns - ds.columns
    # TODO: foreach column in that diff:
    #   guess at column type
    #   if not MYSQL_COL_NAME_PATTERN.match(), suggest sql column name
    return []


  def write_new_definitions(self):

    # write updated yaml file
    self.write_schemadefs()

    # then write out the ddl and migration files

    today_str = datetime.now().strftime("%Y_%m_%d")

    ddl_file = 'covid_hosp.sql'
    migration_file = f"covid_hosp_v{today_str}.sql"

    # TODO: do these with proper python `pathlib.Path` objects
    repo_root = './' # TODO: get this from somewhere
    ddl_file_directory = repo_root + 'src/ddl/'
    migration_file_directory = repo_root + 'src/ddl/migrations/'

    # write newly generated sql definition file
    with open(ddl_file, 'w') as f:
      # TODO
      f.write("\n")

    # write migration file for new columns
    with open(migration_file, 'w') as f:
      # TODO
      # NOTE: we dont have column differences here, this cant stay here without that
      f.write("\n")

    # move files into proper locations
    # UNCOMMENT: os.system("mv -f {ddl_file} {ddl_file_directory}")
    # UNCOMMENT: os.system("mv -f {migration_file} {migration_file_directory")



if __name__ == "__main__":
  chs = CovidHospSomething()
  changed = False

  for ds_name in chs.dataset_names():
    ds = chs.dataset(ds_name)
    new_cols = chs.detect_changes(ds_name)
    if new_cols:
      changed = True
      for col in new_cols:
        chs.add_column(ds_name, col.name, col.dtype)

  if changed:
    print("column changes detected, writing new definition files")
    chs.write_new_definitions()
    sys.exit(1)

  print("no changes detected, exiting")
  sys.exit(0)
