---
title: New Endpoint Tutorial
nav_order: 5
---

# Tutorial: Adding a new API endpoint

**Prerequisite:** this guide assumes that you have read the
[epidata development guide](epidata_development.md).

In this tutorial we'll create a brand new endpoint for the Epidata API:
`fluview_meta`. At a high level, we'll do the following steps:

0. understand the data that we want to surface
1. add the new endpoint to the API server
  - get (transformed) data into a database
  - add internal server maintenance code
  - add frontend code
2. write an integration test for the new endpoint
3. update API documentation for the new endpoint
4. run all unit and integration tests
5. add the new endpoint to the various client libraries

# setup

Follow
[the backend guide](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md)
and [the epidata guide](epidata_development.md) to install Docker and get your
workspace ready for development. Before continuing, your workspace should look
something like the following:

```bash
tree -L 3 .
```

```
.
└── repos
    ├── delphi
    │   ├── delphi-epidata
    │   ├── flu-contest
    │   ├── github-deploy-repo
    │   ├── nowcast
    │   ├── operations
    │   └── utils
    └── undefx
        ├── py3tester
        └── undef-analysis
```
# Adding data to a database
Before we could possibly serve data in an API, we need to retrieve it, clean it,
and store it locally.  This is known as
[ETL](https://en.wikipedia.org/wiki/Extract,_transform,_load), and for any of
the endpoints the code to do this lives in the [acquisition
folder](https://github.com/cmu-delphi/delphi-epidata/tree/dev/src/acquisition).
Retrieving is the least structured of these and depends heavily on the source of
the data. Transforming can be anything from simply cleaning to fit the format of
our database/api, aggregating to higher geographic or temporal levels, to
correcting for knowable anomalies in the data. 
## SQL table design
The first step is determining the format of the tables, which is written in a
[ddl](https://stackoverflow.com/questions/2578194/what-are-ddl-and-dml) and
stored [here](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/ddl/),
for example
[epimetrics](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/ddl/v4_schema.sql)).
Consider prototyping with something like
[dbdiagram](https://dbdiagram.io/d/wastewater_db-6691809a9939893daecc5d57).
Ideally, any redundant values or metadata should be stored in separate related
tables so as to [normalize the
tables](https://en.wikipedia.org/wiki/Database_normalization) and improve
performance. A rule of thumb for these is if you can think of it as a
categorical, it should have a table to record the possible categories.

In addition to the primary table and it's relational tables, it can be useful to
include a loading table to ease addition of new data to the database, a latest
table to speed up access for getting only the latest data, and several views for
TODO reasons.

Another design consideration is the addition of indexes based on likely queries.
### Data format
In many endpoints, dates are represented using integers as `yyyymmdd` for actual
dates and `yyyyww` for epiweeks.
### Versioning
If there's  a possibility you are inserting versions older than latest, it is best practice to include a boolean column in the load table indicating. This column will also be useful for generating a view of the full table
## ETL
After you know the target format, you should start writing methods to perform
each step of the ETL process. Eventually, they should be called within a
`__main__` function in src/acquisition/<endpoint\_name> (ideally
<endpoint\_name>\_main.py). You should partition your code into separate files
for each step in ETL, especially if the transform steps are more than
simply data cleaning.

## Extract
There is not terribly much to be said for extraction; depending on how you get
your data see (TODO list of endpoints based on how they extract data) for an
example, but there is no guarantee that these actually have achieved the optimal
method for that particular method of acquiring data.

One less obvious aspect of the extraction step is validation. Make sure to add
validation checks to the extraction module, with any violations getting recorded
to a logger object.

Another less obvious extraction step is to make sure to record approximately raw
data, stored in a compressed format. This makes recovery from validation or
other errors much easier.
## Transform
If you will be doing significant transformations, consider writing an external
package for that.

One of the more common transformation steps is the removal of redundant
versions. Epimetrics handles this by first exporting the transformed data to
CSVs (for every source, as handled in covidcast-indicators), then comparing with
the previously saved copy of the CSV for differences and only keeping the newer
values. Wastewater handles this entirely within sql by comparing the latest
table with the load table.
<!-- TODO ongoing update -->
## Load
In general, we use [Core
sqlalchemy](https://docs.sqlalchemy.org/en/20/tutorial/index.html) to manage
database connections. The process for loading should roughly be
### Move the data into the load table
The current
recommendation is to use [pandas'
`to_sql`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html)
with the method set to `multi` for the initial insertion into the `load` table as an initial method, for ease of writing.
If this proves too slow, [see
epimetrics](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/acquisition/covidcast/database.py)
for an alternative using approximately raw sql, or write a [custom insert method](https://pandas.pydata.org/docs/user_guide/io.html#io-sql-method) that e.g. uses temporary csv's.
### Move categorical data
After inserting into the load table, any new values for the related tables, such as signal or geo\_type, need to be included.
### Insert load data into the full and latest tables
Fairly straightforward. Note that the keys for the related tables need to be added either during or before inserting into either table.

Note that wastewater removes duplicated values with different versions just after adding the key values from the related tables.
### Remove the inserted data from the load table
Since the id of the load table is used to set the id of the full and latest tables, it is important not to drop or truncate when deleting these rows, since this would reset the index.
# the data

Here's the requirement: we need to quickly surface the most recent "issue"
(epiweek of publication) for the existing [`fluview` endpoint](api/fluview.md).
The existing [`meta` endpoint](api/meta.md) already provides this,
however, it's _very_ slow, and it returns a bunch of unrelated data. The goal
is to extract the subset of metadata pertaining to `fluview` and return just that
data through a new endpoint.

Each row in the `fluview` table contains
[a lot of data](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/ddl/fluview.sql), but we're particularly interested in
the following:

- latest publication date
- latest "issue", which is the publication epiweek
- total size of the table

## Acquire data
If, unlike `fluview` you need to acquire add new data in addition to a new endpoint, you will need to add an appropriate data ingestion method.

Since we're using the `fluview` table, we're piggybacking off of [src/acquisition/fluview](https://github.com/cmu-delphi/delphi-epidata/tree/dev/src/acquisition/fluview). 
To run ingestion, cronicle runs [fluview_update.py](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/acquisition/fluview/fluview_update.py), while the other scripts provide methods for that.
### Secrets
If you are pulling from an API or other source which needs authentication, you will need to add your secret into the backend. How to go about this for new endpoints is TODO.
## Tests
It is recommended to use a dummy database as a part of unit testing; for an example see TODO
## Adding new packages
If for whatever reason you need to add a new dependency TODO
# update the server API

1. create a new file in `/src/server/endpoints/`, e.g. `fluview_meta.py`, or copy an existing one.
2. edit the created file `Blueprint("fluview_meta", __name__)` such that the first argument matches the target endpoint name
3. edit the existing `/src/server/endpoints/__init__.py` to add the newly-created file to the imports (top) and to the list of endpoints (below).


# update the client libraries
<!-- TODO this section is very much out of date-->
There are currently four client libraries. They all need to be updated to make
the new `fluview_meta` endpoint available to callers. The pattern is very
similar for all endpoints so that copy-paste will get you 90% of the way there.

`fluview_meta` is especially simple as it takes no parameters, and consequently,
there is no need to validate parameters. In general, it's a good idea to do
sanity checks on caller inputs prior to sending the request to the API. See
some of the other endpoint implementations (e.g. `fluview`) for an example of
what this looks like.

Here's what we add to each client:

- [`delphi_epidata.js`](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js)
    ```javascript
    // within createEpidataAsync
    return {
      BASE_URL: baseUrl || BASE_URL,
      //...
       /**
        * Fetch FluView metadata
        */
      fluview_meta: () => {
        return _request("fluview_meta", {});
      },
    };
    ```

- [`delphi_epidata.d.ts`](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.d.ts)
    ```typescript
    export interface EpidataFunctions {
      // ...
      fluview_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
    }
    export interface EpidataAsyncFunctions {
      // ...
      fluview_meta(): Promise<EpiDataResponse>;
    }
    ```

- [`delphi_epidata.py`](https://pypi.org/project/delphi-epidata/)

    Note that this file, unlike the others, is released as a public package,
    available to install easily through Python's `pip` tool. That package should
    be updated once the code is committed. However, that is outside of the scope
    of this tutorial.

    ```python
    # Fetch FluView metadata
    @staticmethod
    def fluview_meta():
      """Fetch FluView metadata."""
      # Set up request
      params = {}
      # Make the API call
      return Epidata._request("fluview_meta", params)
    ```

- [`delphi_epidata.R`](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R)

    ```R
    # Fetch FluView metadata
    fluview_meta <- function() {
      # Set up request
      params <- list(
        endpoint = 'fluview_meta'
      )
      # Make the API call
      return(.request(params))
    }
    ```

    **This file requires a second change: updating the list of exported
    functions.** This additional step only applies to this particular client
    library. At the bottom of the file, inside of `return(list(`, add the
    following line to make the function available to callers.

    ```R
    fluview_meta = fluview_meta,
    ```

# add an integration test

Now that we've changed several files, we need to make sure that the changes
work as intended _before_ submitting code for review or committing code to the
repository. Given that the code spans multiple components and languages, this
needs to be an integration test. See more about integration testing in Delphi's
[frontend development guide](https://github.com/cmu-delphi/operations/blob/main/docs/frontend_development.md#integration).

Create an integration test for the new endpoint by creating a new file,
`integrations/server/test_fluview_meta.py`. There's a good amount of
boilerplate, but fortunately, this can be copied _almost_ verbatim from the
[`fluview` endpoint integration test](https://github.com/cmu-delphi/delphi-epidata/blob/main/integrations/server/test_fluview.py).

Include the following pieces:

- top-level docstring (update name to `fluview_meta`)
- the imports section (no changes needed)
- the test class (update name and docstring for `fluview_meta`)
- the methods `setUpClass`, `setUp`, and `tearDown` (no changes needed)

Add the following test method, which creates some dummy data, fetches the new
`fluview_meta` endpoint using the Python client library, and asserts that the
returned value is what we expect.

```python
def test_round_trip(self):
  """Make a simple round-trip with some sample data."""

  # insert dummy data
  self.cur.execute('''
    insert into fluview values
      (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421,
        10, 11, 12, 13, 14, 15),
      (0, "2020-04-28", 202022, 202022, "hhs1", 5, 6, 7, 8, 1.11111, 2.22222,
        20, 21, 22, 23, 24, 25)
  ''')
  self.cnx.commit()

  # make the request
  response = Epidata.fluview_meta()

  # assert that the right data came back
  self.assertEqual(response, {
    'result': 1,
    'epidata': [{
       'latest_update': '2020-04-28',
       'latest_issue': 202022,
       'table_rows': 2,
     }],
    'message': 'success',
  })
```

# write documentation

This consists of two steps: add a new document for the `fluview_meta` endpoint,
and add a new entry to the existing table of endpoints.

Create a new file `docs/api/fluview_meta.md`. Copy as much as needed from other
endpoints, e.g. [the fluview documentation](api/fluview.md). Update the
description, table of return values, and sample code and URLs as needed.

Edit the table of endpoints in [`docs/api/README.md`](api/README.md), adding
the following row in the appropriate place (i.e., next to the row for
`fluview`):

```
| [`fluview_meta`](fluview_meta.md) | FluView Metadata | Summary data about [`fluview`](fluview.md). | no |
```

# run tests

## unit

Finally, we just need to run all new and existing tests. It is recommended to
start with the unit tests because they are faster to build, run, and either
succeed or fail. Follow the
[backend development guide](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md#running-a-container).
In summary:

```bash
# build the image
docker build -t delphi_python \
  -f repos/delphi/operations/dev/docker/python/Dockerfile .

# run epidata unit tests
docker run --rm delphi_python \
  python3 -m undefx.py3tester.py3tester --color \
  repos/delphi/delphi-epidata/tests
```

If all succeeds, output should look like this:

```
[...]

✔ All 48 tests passed! 69% (486/704) coverage.
```

You can also run tests using pytest like this:
```
docker run --rm delphi_python pytest repos/delphi/delphi-epidata/tests/
```
and with pdb enabled like this:
```
docker run -it --rm delphi_python pytest repos/delphi/delphi-epidata/tests/ --pdb
```

## integration

Integration tests require more effort and take longer to set up and run.
However, they allow us to test that various pieces are working together
correctly. Many of these pieces we can't test individually with unit tests
(e.g., database, and the API server), so integration tests are the only way we
can be confident that our changes won't break the API. Follow the [epidata
development guide](epidata_development.md#test). In summary, assuming you have
already built the `delphi_python` image above:

```bash
# build web and database images for epidata
docker build -t delphi_web_epidata\
			-f ./devops/Dockerfile .;\
docker build -t delphi_database_epidata \
  -f repos/delphi/delphi-epidata/dev/docker/database/epidata/Dockerfile .

# launch web and database containers in separate terminals
docker run --rm -p 13306:3306 \
  --network delphi-net --name delphi_database_epidata \
  delphi_database_epidata

docker run --rm -p 10080:80 \
  --network delphi-net --name delphi_web_epidata \
  delphi_web_epidata

# wait for the above containers to initialize (~15 seconds)

# run integration tests
docker run --rm --network delphi-net delphi_python \
  python3 -m undefx.py3tester.py3tester --color \
    repos/delphi/delphi-epidata/integrations
```

If all succeeds, output should look like this. Note also that our new
integration test specifically passed.

```
[...]

delphi.delphi-epidata.integrations.server.test_fluview_meta.FluviewMetaTests.test_round_trip: pass

[...]

✔ All 16 tests passed! 48% (180/372) coverage.
```
You can also run tests using pytest like this:
```
docker run --network delphi-net --rm delphi_python pytest repos/delphi/delphi-epidata/integrations/
```
and with pdb enabled like this:
```
docker run --network delphi-net -it --rm delphi_python pytest repos/delphi/delphi-epidata/integrations/ --pdb
```

# code review and submission

All tests pass, and the changes are working as intended. Now submit the code
for review, (e.g., by opening a pull request on GitHub). For an example, see the
actual
[pull request for the `fluview_meta` endpoint](https://github.com/cmu-delphi/delphi-epidata/pull/93)
created in this tutorial.

Once it's approved, merge the PR, and contact an admin to schedule a release. Once released, the API will begin serving your new endpoint. Go ahead and give it a
try: https://api.delphi.cmu.edu/epidata/fluview_meta/

```
{
  "result": 1,
  "epidata": [
    {
      "latest_update": "2020-04-24",
      "latest_issue": 202016,
      "table_rows": 957673
    }
  ],
  "message": "success"
}
```
