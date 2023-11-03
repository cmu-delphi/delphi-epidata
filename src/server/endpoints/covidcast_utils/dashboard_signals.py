# Provides a list of `(source, signal)` tuples that enumerate those used by the
# COVIDcast Dashboard, found at https://delphi.cmu.edu/covidcast/

# This module uses two files in this current directory as a resource: `descriptions.raw.txt` & `questions.raw.txt`.
# These files are sourced from (and should be kept in sync with) files of the same name from the `www-covidcast`
# repository, found at https://github.com/cmu-delphi/www-covidcast/blob/dev/src/stores/ .  As part of the
# "Create Release" github action for `www-covidcast`, a pull request is created in this repository (`delphi-epidata`)
# with any updates to these files (see:
# https://github.com/cmu-delphi/www-covidcast/blob/dev/.github/workflows/create_release.yml for more details).

from pathlib import Path
import yaml


class DashboardSignals:

  # we use a singleton pattern to prevent reloading files every time this is used
  _instance = None

  def __new__(cls):
    if cls._instance is None:
      # create a singular instance
      cls._instance = cls._instance = super(DashboardSignals, cls).__new__(cls)

      # load sources + signals list from files
      # NOTE: yaml's `load_all` is needed as these txt files are formatted to technically contain "multiple documents"
      srcsigs = []
      module_dir = Path(__file__).parent

      with open(module_dir / 'descriptions.raw.txt', 'r') as f:
        for desc in yaml.safe_load_all(f):
          srcsigs.append( (desc['Id'], desc['Signal']) )
          if 'Overrides' in desc:
            for sub_geo in desc['Overrides']:
              sub_signal = desc['Overrides'][sub_geo]
              srcsigs.append( (sub_signal['Id'], sub_signal['Signal']) )

      source_id = None
      with open(module_dir / 'questions.raw.txt', 'r') as f:
        for ques in yaml.safe_load_all(f):
          if source_id is None:
            # the first entry contains the source 'Id' but doesnt have a 'Signal' key
            source_id = ques['Id'] # NOTE: this should always be 'fb-survey'
          else:
            srcsigs.append( (source_id, ques['Signal']) )

      cls._instance._srcsigs = srcsigs

    return cls._instance


  def srcsig_list(self):
    return self._srcsigs
