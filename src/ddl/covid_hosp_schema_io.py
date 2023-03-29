# TODO: this file and the associated yaml file probably belong in src/common/covid_hosp/ or at least src/common/acquisition/covid_hosp/common/

from datetime import datetime
import re
import sys

# UNCOMMENT: from delphi.epidata.acquisition.covid_hosp.common.utils import Utils

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


class CovidHospSomething:

  YAML_FILENAME = 'covid_hosp_schemadefs.yaml'

  TYPE_MAPPING = {
    'int': int,
    'float': float,
    'str': str,
    'fixedstr', str,
    'intdate': int, # UNCOMMENT: Utils.int_from_date,
    'point': str, # UNCOMMENT: Utils.limited_geocode,
  }

  MYSQL_COL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,64}$')


  def __init__(self):
    self.read_schemadefs()


  def read_schemadefs(self):
    # TODO: put the yaml file inside the package structure and access it there, with something like:
    #   from importlib import resources
    #   import delphi.epidata.common.covid_hosp
    #   self.yaml_content = resources.read_text(delphi.epidata.common.covid_hosp, YAML_FILENAME)
    with open(CovidHospSomething.YAML_FILENAME, 'r') as yaml_file:
      self.yaml_content = yaml_load(yaml_file, preserve_quotes=True)
    return self.yaml_content


  def write_schemadefs(self, filename=CovidHospSomething.YAML_FILENAME):
    with open(filename, 'w') as yaml_file:
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
      yield {'name': name, 'sql_name': sql_name, 'dtype': dtype, 'col_width:' col_width, 'marshaller': CovidHospSomething.TYPE_MAPPING[dtype]}


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
    today_str = datetime.now().strftime("%Y_%m_%d")

    yaml_file = CovidHospSomething.YAML_FILENAME
    ddl_file = 'covid_hosp.sql'
    migration_file = f"covid_hosp_v{today_str}.sql"

    # TODO: do these with proper python `pathlib.Path` objects
    repo_root = './'
    yaml_file_directory = repo_root + 'src/ddl/'
    ddl_file_directory = repo_root + 'src/ddl/'
    migration_file_directory = repo_root + 'src/ddl/migrations/'

    # write updated yaml file
    self.write_schemadefs()

    # write newly generated sql definition file
    with open(ddl_file, 'w') as f:
      # TODO
      f.write("\n")

    # write migration file for new columns
    with open(migration_file, 'w') as f:
      # TODO
      f.write("\n")

    # move files into proper locations
    # UNCOMMENT: os.system(f"mv -f {yaml_file} {yaml_file_directory}")
    # UNCOMMENT: os.system("mv -f {ddl_file} {ddl_file_directory}")
    # UNCOMMENT: os.system("mv -f {migration_file} {migration_file_directory")



if __name__ == "__main__":
  chs = CovidHospSomething()
  changed = False

  for ds_name in chs.datasets():
    ds = chs.dataset(ds_name)
    new_cols = chs.detect_changes(ds_name)
    if new_cols:
      changed = True
      for col in new_cols:
        chs.add_column(ds_name, col.name, col.dtype)

  if changed:
    chs.write_new_definitions()
    sys.exit(1)

  sys.exit(0)
