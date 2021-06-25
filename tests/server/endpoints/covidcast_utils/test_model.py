from numpy.lib.utils import source
from pandas import DataFrame, to_datetime, date_range
from pandas.testing import assert_frame_equal

from delphi.epidata.server._params import SourceSignalPair
from delphi.epidata.server.endpoints.covidcast_utils.model import create_source_signal_derivation_mapper, data_signals_by_key

class TestStreaming:
    def test_create_source_signal_derivation_mapper(self):
        source_signal_pair = SourceSignalPair("jhu-csse", True)
        breakpoint()
        dm = create_source_signal_derivation_mapper([source_signal_pair])
        assert 2

    def test_fetch_derivable_signal(self):
        ...
        # assert fetch_derivable_signal(SourceSignalPair("google-symptoms", "ageusia_smoothed_search"))[0] == SourceSignalPair("google-symptoms", "ageusia_raw_search")
        # assert fetch_derivable_signal(SourceSignalPair("google-symptoms", "not_derivable"))[0] == SourceSignalPair("google-symptoms", "not_derivable")
