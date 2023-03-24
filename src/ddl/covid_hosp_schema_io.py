
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



def read_schemadefs():
  with open("covid_hosp_schemadefs.yaml", 'r') as yaml_file:
    yaml_content = yaml_load(yaml_file, preserve_quotes=True)
  return yaml_content


def write_schemadefs(yaml_content):
  # this block replaces duplicated column names with null/None/~
  # (when same name is shared between SQL representation and python/source representation)
  for dataset in yaml_content:
    for col in yaml_content[dataset]['ORDERED_CSV_COLUMNS']:
      if col[0]==col[1]:
        col[1] = None
  with open("covid_hosp_schemadefs__out.yaml", 'w') as yaml_file:
    yaml_dump(yaml_content, yaml_file, width=200)
    # NOTE: `width` specification is to prevent dump from splitting long lines
    # TODO: consider `block_seq_indent=2` to make list under ORDERED_CSV_COLUMNS look a little better


yaml_content = read_schemadefs()
write_schemadefs(yaml_content)

# TODO: figure out what to do wrt splitting lines (maybe split line inside ORDERED_CSV_COLUMNS list between column name and column rename?!)
