"""Integration tests for acquisition of COVID hospitalization facility."""

# standard library
import unittest
from unittest.mock import MagicMock

# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database
from delphi.epidata.acquisition.covid_hosp.common.test_utils import (
    UnitTestUtils,
)
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covid_hosp.facility.update import Update
import delphi.operations.secrets as secrets

# third party
from freezegun import freeze_time

# py3tester coverage target (equivalent to `import *`)
__test_target__ = "delphi.epidata.acquisition.covid_hosp.facility.update"

NEWLINE = "\n"


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        """Perform per-test setup."""

        # configure test data
        self.test_utils = UnitTestUtils(__file__)

        # use the local instance of the Epidata API
        # Default value for BASE_URL is "https://delphi.cmu.edu/epidata/api.php" and None for auth
        Epidata.BASE_URL = "http://delphi_web_epidata/epidata/api.php"
        Epidata.auth = ("epidata", "key")

        # use the local instance of the epidata database
        secrets.db.host = "delphi_database_epidata"
        secrets.db.epi = ("user", "pass")

        # clear relevant tables
        with Database.connect() as db:
            with db.new_cursor() as cur:
                cur.execute("truncate table covid_hosp_facility")
                cur.execute("truncate table covid_hosp_meta")
                cur.execute("truncate table api_user")
                cur.execute(
                    'insert into api_user(api_key, email, roles, tracking, registered) values("key","test@gmail.com", "", 1, 1)'
                )

    @freeze_time("2021-03-16")
    def test_acquire_dataset(self):
        """Acquire a new dataset."""

        # only mock out network calls to external hosts
        mock_network = MagicMock()
        mock_network.fetch_metadata.return_value = (
            self.test_utils.load_sample_metadata()
        )
        mock_network.fetch_dataset.return_value = (
            self.test_utils.load_sample_dataset()
        )

        # make sure the data does not yet exist
        with self.subTest(name="no data yet"):
            response = Epidata.covid_hosp_facility(
                "450822", Epidata.range(20200101, 20210101)
            )
            self.assertEqual(response["result"], -2, response)

        # acquire sample data into local database
        with self.subTest(name="first acquisition"):
            acquired = Update.run(network=mock_network)
            self.assertTrue(acquired)

        # make sure the data now exists
        with self.subTest(name="initial data checks"):
            expected_spotchecks = {
                "hospital_pk": "450822",
                "collection_week": 20201030,
                "publication_date": 20210315,
                "previous_day_total_ed_visits_7_day_sum": 536,
                "total_personnel_covid_vaccinated_doses_all_7_day_sum": 18,
                "total_beds_7_day_avg": 69.3,
                "previous_day_admission_influenza_confirmed_7_day_sum": -999999,
            }
            response = Epidata.covid_hosp_facility(
                "450822", Epidata.range(20200101, 20210101)
            )
            self.assertEqual(response["result"], 1)
            self.assertEqual(len(response["epidata"]), 1)
            row = response["epidata"][0]
            for k, v in expected_spotchecks.items():
                self.assertTrue(
                    k in row,
                    f"no '{k}' in row:\n{NEWLINE.join(sorted(row.keys()))}",
                )
                if isinstance(v, float):
                    self.assertAlmostEqual(
                        row[k], v, f"row[{k}] is {row[k]} not {v}"
                    )
                else:
                    self.assertEqual(
                        row[k], v, f"row[{k}] is {row[k]} not {v}"
                    )

            # expect 113 fields per row (114 database columns, except `id`)
            self.assertEqual(len(row), 113)

        # re-acquisition of the same dataset should be a no-op
        with self.subTest(name="second acquisition"):
            acquired = Update.run(network=mock_network)
            self.assertFalse(acquired)

        # make sure the data still exists
        with self.subTest(name="final data checks"):
            response = Epidata.covid_hosp_facility(
                "450822", Epidata.range(20200101, 20210101)
            )
            self.assertEqual(response["result"], 1)
            self.assertEqual(len(response["epidata"]), 1)

    @freeze_time("2021-03-16")
    def test_facility_lookup(self):
        """Lookup facilities using various filters."""

        # only mock out network calls to external hosts
        mock_network = MagicMock()
        mock_network.fetch_metadata.return_value = (
            self.test_utils.load_sample_metadata()
        )
        mock_network.fetch_dataset.return_value = (
            self.test_utils.load_sample_dataset()
        )

        # acquire sample data into local database
        with self.subTest(name="first acquisition"):
            acquired = Update.run(network=mock_network)
            self.assertTrue(acquired)

        # texas ground truth, sorted by `hospital_pk`
        # see sample data at testdata/acquisition/covid_hosp/facility/dataset_old.csv
        texas_hospitals = [
            {
                "hospital_pk": "450771",
                "state": "TX",
                "ccn": "450771",
                "hospital_name": "TEXAS HEALTH PRESBYTERIAN HOSPITAL PLANO",
                "address": "6200 W PARKER RD",
                "city": "PLANO",
                "zip": "75093",
                "hospital_subtype": "Short Term",
                "fips_code": "48085",
                "is_metro_micro": 1,
            },
            {
                "hospital_pk": "450822",
                "state": "TX",
                "ccn": "450822",
                "hospital_name": "MEDICAL CITY LAS COLINAS",
                "address": "6800 N MACARTHUR BLVD",
                "city": "IRVING",
                "zip": "75039",
                "hospital_subtype": "Short Term",
                "fips_code": "48113",
                "is_metro_micro": 1,
            },
            {
                "hospital_pk": "451329",
                "state": "TX",
                "ccn": "451329",
                "hospital_name": "RANKIN HOSPITAL MEDICAL CLINIC",
                "address": "1611 SPUR 576",
                "city": "RANKIN",
                "zip": "79778",
                "hospital_subtype": "Critical Access Hospitals",
                "fips_code": "48461",
                "is_metro_micro": 0,
            },
        ]

        with self.subTest(name="by state"):
            response = Epidata.covid_hosp_facility_lookup(state="tx")
            self.assertEqual(response["epidata"], texas_hospitals)

        with self.subTest(name="by ccn"):
            response = Epidata.covid_hosp_facility_lookup(ccn="450771")
            self.assertEqual(response["epidata"], texas_hospitals[0:1])

        with self.subTest(name="by city"):
            response = Epidata.covid_hosp_facility_lookup(city="irving")
            self.assertEqual(response["epidata"], texas_hospitals[1:2])

        with self.subTest(name="by zip"):
            response = Epidata.covid_hosp_facility_lookup(zip="79778")
            self.assertEqual(response["epidata"], texas_hospitals[2:3])

        with self.subTest(name="by fips_code"):
            response = Epidata.covid_hosp_facility_lookup(fips_code="48085")
            self.assertEqual(response["epidata"], texas_hospitals[0:1])

        with self.subTest(name="no results"):
            response = Epidata.covid_hosp_facility_lookup(state="not a state")
            self.assertEqual(response["result"], -2)
