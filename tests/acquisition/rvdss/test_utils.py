"""Unit tests for rvdss/utils.py."""

import pytest

from delphi.epidata.acquisition.rvdss.utils import abbreviate_virus, create_geo_types

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.rvdss.utils"


class TestUtils:
    def test_syntax(self):
        """This no-op test ensures that syntax is valid."""
        pass

    def test_abbreviate_virus(self):
    	assert abbreviate_virus("influenza") == "flu" # normal case
    	assert abbreviate_virus("flu") == "flu" # already abbreviated

    def test_create_geo_types(self):
        assert create_geo_types("canada","lab") == "nation"
        assert create_geo_types("bc","lab") == "region"
        assert create_geo_types("random lab","lab") == "lab"
        assert create_geo_types("Canada","province") == "province" #lowercase handling happens upstream