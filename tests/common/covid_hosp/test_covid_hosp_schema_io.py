from pathlib import Path

import unittest

from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething


# py3tester coverage target (equivalent to `import *`)
__test_target__ = "delphi.epidata.common.covid_hosp.covid_hosp_schema_io"


class TestCovidHospSchemaIo(unittest.TestCase):
    chs = CovidHospSomething(str(Path(__file__).parent.absolute()) + "/test_covid_hosp_schemadefs.yaml")

    def test_get_ds_info(self):
        TABLE_NAME, KEY_COLS, AGGREGATE_KEY_COLS, ORDERED_CSV_COLUMNS = self.chs.get_ds_info("covid_hosp_facility")
        assert TABLE_NAME == "covid_hosp_facility"
        assert KEY_COLS == ["hospital_pk", "collection_week"]
        assert AGGREGATE_KEY_COLS == ["address", "ccn", "city", "fips_code", "geocoded_hospital_address", "hhs_ids", "hospital_name", "hospital_pk", "hospital_subtype", "is_metro_micro", "state", "zip"]
        assert ORDERED_CSV_COLUMNS == []
