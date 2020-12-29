from . import (
    covidcast_meta,
    flusurv,
    fluview,
    covid_hosp_facility_lookup,
    covid_hosp_facility,
)

endpoints = [
    covidcast_meta,
    flusurv,
    fluview,
    covid_hosp_facility_lookup,
    covid_hosp_facility,
]

__all__ = ["endpoints"]
