# common

This directory contains somewhat generic code that's used by multiple
`covid_hosp` scrapers. This includes code that's used by multiple unit and
integration tests (see `test_utils.py`), even when that code isn't directly
used in production.

Since the operational difference between `covid_hosp` datasets is very small,
most of the actual logic is contained here.
