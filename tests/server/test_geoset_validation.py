"""Regression tests for GeoSet fail-closed geo_type validation (issue #1803).

GeoSet previously skipped geo_value allowlisting entirely for any geo_type
not in its translator, so attacker-controlled type/value pairs (e.g.
``geo=bogus:x'-- DROP``) were accepted. Unknown geo types must now be
rejected with a 400, and the ``fips``/``dma`` aliases accepted by the API
must have their values validated as well.
"""

# standard library
import unittest

from delphi.epidata.server._common import app
from delphi.epidata.server._params import GeoSet
from delphi.epidata.server._exceptions import ValidationFailedException

# py3tester coverage target
__test_target__ = "delphi.epidata.server._params"


class GeoSetValidationTests(unittest.TestCase):
    """GeoSet must fail closed on geo types it cannot validate."""

    def test_unknown_geo_type_rejected(self):
        with app.test_request_context("/?format=json"):
            # the exact bypass from the issue report
            with self.assertRaises(ValidationFailedException):
                GeoSet("bogus", ["x'-- DROP"])
            with self.assertRaises(ValidationFailedException):
                GeoSet("nation`--", ["x"])
            # fail closed even when no concrete values are supplied
            with self.assertRaises(ValidationFailedException):
                GeoSet("bogus", True)

    def test_fips_alias_values_validated(self):
        with app.test_request_context("/?format=json"):
            with self.assertRaises(ValidationFailedException):
                GeoSet("fips", ["99999"])
            with self.assertRaises(ValidationFailedException):
                GeoSet("fips", ["x'-- DROP"])
            # legitimate county FIPS codes are still accepted
            GeoSet("fips", ["04019", "19143"])
            GeoSet("fips", True)

    def test_dma_values_validated(self):
        with app.test_request_context("/?format=json"):
            # outside the acquisition sanity range (450-950)
            with self.assertRaises(ValidationFailedException):
                GeoSet("dma", ["1"])
            with self.assertRaises(ValidationFailedException):
                GeoSet("dma", ["not-a-number"])
            # legitimate DMA codes are still accepted
            GeoSet("dma", ["500"])
            GeoSet("dma", True)

    def test_known_geo_types_unchanged(self):
        with app.test_request_context("/?format=json"):
            GeoSet("county", ["04019"])
            GeoSet("state", ["ca"])
            GeoSet("nation", ["us"])
            GeoSet("county", True)
            # invalid values for known types are still rejected
            with self.assertRaises(ValidationFailedException):
                GeoSet("county", ["not-a-fips"])
