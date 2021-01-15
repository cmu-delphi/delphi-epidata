---
title: New Endpoint Tutorial
nav_order: 5
---

# Tutorial: Adding a new API endpoint

**Prerequisite:** this guide assumes that you have read the
[epidata development guide](epidata_development.md).

In this tutorial we'll create a brand new endpoint for the Epidata API:
`fluview_meta`. At a high level, we'll do the following steps:

1. understand the data that we want to surface
2. add the new endpoint to `api.php`
3. add the new endpoint to the various client libraries
4. write an integration test for the new endpoint
5. update API documentation for the new endpoint
6. run all unit and integration tests

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

# the data

Here's the requirement: we need to quickly surface the most recent "issue"
(epiweek of publication) for the existing [`fluview` endpoint](api/fluview.md).
The existing [`meta` endpoint](api/meta.md) already provides this,
however, it's _very_ slow, and it returns a bunch of unrelated data. The goal
is to extract the subset of metadata pertaining to `fluview` and return just that
data through a new endpoint.

Each row in the `fluview` table contains
[a lot of data](../src/ddl/fluview.sql), but we're particularly interested in
the following:

- latest publication date
- latest "issue", which is the publication epiweek
- total size of the table

# update the server

Open [`api.php`](../src/server/api.php) and navigate to the bottom where we see
line like `if($endpoint === 'NAME') { ... }`. Right below the `if` block for
`if($endpoint === 'fluview')`, add a new `if else` block for our new endpoint:

```php
else if($endpoint === 'fluview_meta') {
 // get the data
 $epidata = meta_fluview();
 store_result($data, $epidata);
}
```

Fortunately, the function `meta_fluview()` is already defined, so we can just
reuse it. (It's used by the `meta` endpoint as mentioned above.) In general,
you will likely need to define a new function named like
`get_SOURCE(params...)`, especially if you're reading from a new database
table.

# update the client libraries

There are currently four client libraries. They all need to be updated to make
the new `fluview_meta` endpoint available to callers. The pattern is very
similar for all endpoints so that copy-paste will get you 90% of the way there.

`fluview_meta` is especially simple as it takes no parameters, and consequently,
there is no need to validate parameters. In general, it's a good idea to do
sanity checks on caller inputs prior to sending the request to the API. See
some of the other endpoint implementations (e.g. `fluview`) for an example of
what this looks like.

Here's what we add to each client:

- [`delphi_epidata.coffee`](../src/client/delphi_epidata.coffee)

    ```coffeescript
    # Fetch FluView metadata
    @fluview_meta: (callback) ->
      # Set up request
      params =
        'endpoint': 'fluview_meta'
      # Make the API call
      _request(callback, params)
    ```

- [`delphi_epidata.js`](../src/client/delphi_epidata.js)

    Note that this file _can and should be generated from
    `delphi_epidata.coffee`_. However, for trivial changes, like the addition
    of this very simple endpoint, it may be slightly faster, _though
    error-prone_, to just update the JavaScript manually.

    ```javascript
    Epidata.fluview_meta = function(callback) {
      var params;
      params = {
        'endpoint': 'fluview_meta'
      };
      return _request(callback, params);
    };
    ```

- [`delphi_epidata.py`](../src/client/delphi_epidata.py)

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
      params = {
        'endpoint': 'fluview_meta',
      }
      # Make the API call
      return Epidata._request(params)
    ```

- [`delphi_epidata.R`](../src/client/delphi_epidata.R)

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
[`fluview` endpoint integration test](../integrations/server/test_fluview.py).

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
docker build -t delphi_web \
  -f repos/delphi/operations/dev/docker/web/Dockerfile .
docker build -t delphi_web_epidata \
  -f repos/delphi/delphi-epidata/dev/docker/web/epidata/Dockerfile .
docker build -t delphi_database \
  -f repos/delphi/operations/dev/docker/database/Dockerfile .
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

Once it's approved, commit the code. Within a short amount of time (usually ~30
seconds), the API will begin serving your new endpoint. Go ahead and give it a
try: https://delphi.midas.cs.cmu.edu/epidata/api.php?endpoint=fluview_meta

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
