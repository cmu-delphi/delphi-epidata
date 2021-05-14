"""Unit tests for delphi_epidata.py."""

# standard library
import unittest
import time
from datetime import date

import pandas as pd

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'

from delphi.epidata.client.delphi_epidata import Epidata

class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  # TODO: Unit tests still need to be written. This no-op test will pass unless
  # the target file can't be loaded. In effect, it's a syntax checker.
  def test_syntax(self):
    pass
