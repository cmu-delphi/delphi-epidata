"""Unit tests for rvdss/utils.py."""

import pytest

from delphi.epidata.acquisition.rvdss.utils import abbreviate_virus

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.rvdss.utils"


class TestUtils:
    def test_syntax(self):
        """This no-op test ensures that syntax is valid."""
        pass

    def test_abbreviate_virus(self):
    	assert abbreviate_virus("influenza") == "flu" # normal case
    	assert abbreviate_virus("flu") == "flu" # already abbreviated
