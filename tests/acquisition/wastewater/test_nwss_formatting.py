import pytest
from structlog.testing import capture_logs
from delphi_utils import get_structured_logger

from pandas.testing import assert_frame_equal
from acquisition.wastewater.nwss_csv import (
    format_nwss_data,
    key_plot_id_parse,
    pull_from_file,
)
import pandas as pd


@pytest.fixture(name="logger")
def fixture_logger(tmp_path):
    logger = get_structured_logger(filename=tmp_path / "log_output.txt")
    return logger


class TestKeyPlotIdFormatting:
    def test_typical_key_plot_id_input(self, logger):
        """A couple of examples of typical behavior."""
        typical_examples = pd.Series(
            [
                "NWSS_mi_889_Before treatment plant_122_raw wastewater",
                "NWSS_wi_2528_Before treatment plant_636_raw wastewater",
                "WWS_fl_2359_Before treatment plant_553_post grit removal",
                "NWSS_il_606_Treatment plant_raw wastewater",  # no sample loc specify
                "CDC_VERILY_la_1651_Treatment plant_post grit removal",  # verily
            ]
        )
        result = pd.DataFrame(
            data={
                "key_plot_id": typical_examples,
                "provider": ["NWSS", "NWSS", "WWS", "NWSS", "CDC_VERILY"],
                "wwtp_jurisdiction": ["mi", "wi", "fl", "il", "la"],
                "wwtp_id": [889, 2528, 2359, 606, 1651],
                "sample_location": [
                    "Before treatment plant",
                    "Before treatment plant",
                    "Before treatment plant",
                    "Treatment plant",
                    "Treatment plant",
                ],
                "sample_location_specify": [122, 636, 553, -1, -1],
                "sample_method": [
                    "raw wastewater",
                    "raw wastewater",
                    "post grit removal",
                    "raw wastewater",
                    "post grit removal",
                ],
            }
        )
        result = result.set_index("key_plot_id")
        result = result.astype(
            dtype={
                "provider": "category",
                "wwtp_jurisdiction": "category",
                "wwtp_id": "Int32",
                "sample_location": "category",
                "sample_location_specify": "Int32",
                "sample_method": "category",
            }
        )
        assert_frame_equal(result, key_plot_id_parse(typical_examples, logger))

    def test_edge_key_plot_id_input(self, logger):
        """Examples that might break the regex but shouldn't."""
        examples = pd.Series(
            [
                "Some_name_with_lots_of_spaces_wa_88_Before treatment plant_348_raw wastewater",
                "provider_is_broken_va_258_Treatment plant_raw wastewater",
            ]
        )
        expected_output = pd.DataFrame(
            data={
                "key_plot_id": examples,
                "provider": ["Some_name_with_lots_of_spaces", "provider_is_broken"],
                "wwtp_jurisdiction": ["wa", "va"],
                "wwtp_id": [88, 258],
                "sample_location": ["Before treatment plant", "Treatment plant"],
                "sample_location_specify": [348, -1],
                "sample_method": ["raw wastewater", "raw wastewater"],
            }
        )
        expected_output = expected_output.set_index("key_plot_id")
        expected_output = expected_output.astype(
            dtype={
                "provider": "category",
                "wwtp_jurisdiction": "category",
                "wwtp_id": "Int32",
                "sample_location": "category",
                "sample_location_specify": "Int32",
                "sample_method": "category",
            }
        )
        expected_output.dtypes
        processed_names = key_plot_id_parse(examples, logger)
        assert_frame_equal(expected_output, key_plot_id_parse(examples, logger))

    ########### breaking cases #############
    def test_treatment_plant_numbering(self, logger, tmp_path):
        """tests for sample location numbering"""
        # shouldn't have a number for a treatment plant
        examples = pd.Series(
            [
                "NWSS_wa_88_Treatment plant_348_raw wastewater",
                "NWSS_wa_88_Maybe treatment plant_348_raw wastewater",
                "NWSS_wa_88_Before treatment plant_-1_raw wastewater",
                "NWSS_wa_88_Treatment plant_-10_raw wastewater",
            ],
            name="key_plot_id",
        )
        with capture_logs() as cap_logs:
            key_plot_id_parse(examples, logger)

        assert (
            cap_logs[0]["sample_locations"]
            == pd.Index(
                ["Before treatment plant", "Maybe treatment plant", "Treatment plant"],
                dtype="object",
            )
        ).all()
        assert cap_logs[0]["event"] == "There is a new value for sample location"
        assert cap_logs[0]["log_level"] == "error"

        # treatment plants with sample location specified when they shouldn't
        assert (cap_logs[1]["key_plot_ids"] == examples[0:1]).all()
        assert (
            cap_logs[1]["event"]
            == "There are samples at treatment plants which have the sample location specified"
        )
        assert cap_logs[1]["log_level"] == "error"

        # the opposite case: unspecified sample location when it's before the
        # treatment plant
        assert (cap_logs[2]["key_plot_ids"] == examples[2:3]).all()
        assert (
            cap_logs[2]["event"]
            == "There are samples before treatment plants which don't have the sample location specified"
        )
        assert cap_logs[2]["log_level"] == "error"

        # too negative
        assert (cap_logs[3]["key_plot_ids"] == examples[3:4]).all()
        assert cap_logs[3]["event"] == "sample_location_specify has an unexpected value"
        assert cap_logs[3]["log_level"] == "error"

    def test_wwtp_id_assumptions(self, logger, tmp_path):
        """Negative, missing, or too large wwtp_id's"""
        # shouldn't have a number for a treatment plant
        examples = pd.Series(
            [
                "NWSS_wa_-88_Before treatment plant_348_raw wastewater",
                f"NWSS_wa_{10_001}_Before treatment plant_348_raw wastewater",
                "NWSS_wa_NA_Before treatment plant_348_raw wastewater",
            ],
            name="key_plot_id",
        )
        with capture_logs() as cap_logs:
            key_plot_id_parse(examples, logger)

        # negative values
        assert (examples[0:1] == cap_logs[0]["key_plot_ids"]).all()
        assert cap_logs[0]["event"] == "the wwtp_id's have negative values"
        assert cap_logs[0]["log_level"] == "error"

        # NA value
        assert (examples[2:3] == cap_logs[1]["key_plot_ids"]).all()
        assert cap_logs[1]["event"] == "the wwtp_id's have NA values"
        assert cap_logs[1]["log_level"] == "error"

        # too large (warning only)
        assert (examples[1:2] == cap_logs[2]["key_plot_ids"]).all()
        assert cap_logs[2]["event"] == "wwtp_id values are over 10,000"
        assert cap_logs[2]["log_level"] == "warning"
