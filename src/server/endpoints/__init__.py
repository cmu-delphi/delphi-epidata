from . import (
    covidcast_meta,
    flusurv,
    fluview,
    covidcast,
    covid_hosp_facility_lookup,
    covid_hosp_facility,
    covid_hosp_state_timeseries,
)

endpoints = [
    covidcast,
    covidcast_meta,
    flusurv,
    fluview,
    covid_hosp_facility_lookup,
    covid_hosp_facility,
    covid_hosp_state_timeseries,
]

__all__ = ["endpoints"]
