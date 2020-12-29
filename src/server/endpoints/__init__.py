from . import (
    covid_hosp_facility_lookup,
    covid_hosp_facility,
    covid_hosp_state_timeseries,
    covidcast_meta,
    covidcast,
    flusurv,
    fluview,
    meta_afhsb,
    meta_norostat,
    meta,
)

endpoints = [
    covid_hosp_facility_lookup,
    covid_hosp_facility,
    covid_hosp_state_timeseries,
    covidcast_meta,
    covidcast,
    flusurv,
    fluview,
    meta_afhsb,
    meta_norostat,
    meta,
]

__all__ = ["endpoints"]
