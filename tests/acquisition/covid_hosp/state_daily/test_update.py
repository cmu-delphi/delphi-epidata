"""Unit tests for update.py."""

# standard library
import unittest
from unittest.mock import patch
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.update import Update

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.update'


class UpdateTests(unittest.TestCase):

  def test_run(self):
    """Acquire a new dataset."""

    with patch.object(Utils, 'update_dataset') as mock_update_dataset:
      mock_update_dataset.return_value = sentinel.result

      result = Update.run()

      self.assertEqual(result, sentinel.result)
      mock_update_dataset.assert_called_once()
