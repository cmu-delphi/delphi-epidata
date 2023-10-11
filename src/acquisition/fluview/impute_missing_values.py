"""
===============
=== Purpose ===
===============

Imputes missing versioned ILINet data from publicly available data.

This file replaces state_ili_update.py, which, together with state_info.py,
performed a similar function prior to 2017w40 when FluView didn't include any
state-level data.

See also:
  - fluview.py
  - state_ili_update.py
  - state_info.py


=======================
=== Data Dictionary ===
=======================

`fluview_imputed` is the table where the imputed ILI data is stored.
+---------------+-------------+------+-----+---------+----------------+
| Field         | Type        | Null | Key | Default | Extra          |
+---------------+-------------+------+-----+---------+----------------+
| id            | int(11)     | NO   | PRI | NULL    | auto_increment |
| issue         | int(11)     | NO   | MUL | NULL    |                |
| epiweek       | int(11)     | NO   | MUL | NULL    |                |
| region        | varchar(12) | NO   | MUL | NULL    |                |
| lag           | int(11)     | NO   | MUL | NULL    |                |
| num_ili       | int(11)     | NO   |     | NULL    |                |
| num_patients  | int(11)     | NO   |     | NULL    |                |
| num_providers | int(11)     | NO   |     | NULL    |                |
| ili           | double      | NO   |     | NULL    |                |
+---------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
  and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
region: the name of the location (e.g. 'fl', 'la', 'ms', 'pr', 'vi', 'ny')
lag: number of weeks between `epiweek` and `issue`
num_ili: the number of ILI cases (numerator)
num_patients: the total number of patients (denominator)
num_providers: the number of reporting healthcare providers
ili: unweighted percent ILI
"""

# standard library
import argparse

# third party
import mysql.connector
import numpy as np

# first party
import delphi.operations.secrets as secrets
from delphi.utils.epiweek import delta_epiweeks
from delphi.utils.geo.locations import Locations


class Database:
    """Database wrapper and abstraction layer."""

    class Sql:
        """Container for SQL constants."""

        # Count the total number of imputed rows.
        count_rows = """
        SELECT
          count(1) `num`
        FROM
          `fluview_imputed`
        """

        # Find (issue, epiweek) pairs that exist in table `fluview` but not in
        # table `fluview_imputed`. Note that only issues >= 201740 are selected
        # because that's when CDC first started posting state-level ILINet data.
        # This assumes that `fluview` is always missing at least one location.
        find_missing_rows = """
        SELECT
          fv.`issue`, fv.`epiweek`
        FROM (
          SELECT
            `issue`, `epiweek`
          FROM
            `fluview`
          WHERE
            `issue` >= 201740
          GROUP BY
            `issue`, `epiweek`
        ) fv
        LEFT JOIN (
          SELECT
            `issue`, `epiweek`
          FROM
            `fluview_imputed`
          GROUP BY
            `issue`, `epiweek`
        ) fvi
        ON
          fvi.`issue` = fv.`issue` AND fvi.`epiweek` = fv.`epiweek`
        WHERE
          fvi.`issue` IS NULL
        """

        # Read all location rows from the `fluview` table for a given issue and
        # epiweek.
        get_known_values = """
        SELECT
          `region`, `num_ili`, `num_patients`, `num_providers`
        FROM
          `fluview`
        WHERE
          `issue` = %s AND `epiweek` = %s
        """

        # Insert location rows into the `fluview_imputed` table for a given issue
        # and epiweek.
        add_imputed_values = """
        INSERT INTO
          `fluview_imputed` (
            `issue`,
            `epiweek`,
            `region`,
            `lag`,
            `num_ili`,
            `num_patients`,
            `num_providers`,
            `ili`
          )
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s)
        """

    def connect(self):
        """Connect to the database."""
        u, p = secrets.db.epi
        self.cnx = mysql.connector.connect(user=u, password=p, database="epidata", host=secrets.db.host)
        self.cur = self.cnx.cursor()

    def close(self, commit):
        """
        Close the connection to the database, committing or rolling back changes as
        indicated.
        """
        self.cur.close()
        if commit:
            self.cnx.commit()
        else:
            print("test mode, not committing")
        self.cnx.close()

    def count_rows(self):
        """Count and return the number of rows in the `fluview_imputed` table."""
        self.cur.execute(Database.Sql.count_rows)
        for (num,) in self.cur:
            return num

    def find_missing_rows(self):
        """
        Find rows that still have missing values. Each missing row is uniquely
        identified by an (issue, epiweek, location) tuple. This function finds the
        first two.
        """

        self.cur.execute(Database.Sql.find_missing_rows)
        return [(issue, epiweek) for (issue, epiweek) in self.cur]

    def get_known_values(self, issue, epiweek):
        """
        Fetch ILINet data for all locations available for the given issue and
        epiweek. The returned value is a dict mapping from locations to ILI data.
        """

        self.cur.execute(Database.Sql.get_known_values, (issue, epiweek))
        return {loc: (n_ili, n_pat, n_prov) for (loc, n_ili, n_pat, n_prov) in self.cur}

    def add_imputed_values(self, issue, epiweek, imputed):
        """
        Store imputed ILINet data for the given locations on the given issue and
        epiweek. The imputed value is a dict mapping from locations to ILI data.
        """

        for loc in imputed.keys():
            lag, n_ili, n_pat, n_prov, ili = imputed[loc]
            args = (issue, epiweek, loc, lag, n_ili, n_pat, n_prov, ili)
            self.cur.execute(Database.Sql.add_imputed_values, args)


class StatespaceException(Exception):
    """Used to indicate that imputation is not possible with the given inputs."""


def get_location_graph():
    """
    Return a matrix where rows represent regions, columns represent atoms, and
    each entry is a 1 if the region contains the atom, otherwise 0. The
    corresponding lists of regions and atoms are also returned.
    """

    regions = sorted(Locations.region_list)
    atoms = sorted(Locations.atom_list)
    graph = np.zeros((len(regions), len(atoms)))
    for i, r in enumerate(regions):
        for a in Locations.region_map[r]:
            j = atoms.index(a)
            graph[i, j] = 1
    return graph, regions, atoms


def get_fusion_parameters(known_locations):
    """
    Return a matrix that fuses known ILI values into unknown ILI values. The
    corresponding lists of known and unknown locations are also returned.

    The goal is to infer ILI data in all locations, given ILI data in some
    partial set of locations. This function takes a sensor fusion approach.

    Let $z$ be a column vector of values in reported locations. Let $y$ be the
    desired column vector of values in unreported locations. With matrices $H$
    (mapping from latent state to reported values), $W$ (mapping from latent
    state to unreported values), and $R = I$ (covariance, which is identity):

      $y = W (H^T R^{-1} H)^{-1} H^T R^{-1} z$
      $y = W (H^T H)^{-1} H^T z$

    This is equavalent to OLS regression with an added translation from atomic
    locations to missing locations. Unknown values are computed as a linear
    combination of known values.
    """

    graph, regions, atoms = get_location_graph()
    is_known = np.array([r in known_locations for r in regions])
    is_unknown = np.logical_not(is_known)
    if not np.any(is_known):
        raise StatespaceException("no values are known")
    if not np.any(is_unknown):
        raise StatespaceException("no values are unknown")

    H = graph[is_known, :]
    W = graph[is_unknown, :]
    if np.linalg.matrix_rank(H) != len(atoms):
        raise StatespaceException("system is underdetermined")

    HtH = np.dot(H.T, H)
    HtH_inv = np.linalg.inv(HtH)
    H_pseudo_inv = np.dot(HtH_inv, H.T)
    fuser = np.dot(W, H_pseudo_inv)

    locations = np.array(regions)
    filter_locations = lambda selected: list(map(str, locations[selected]))
    return fuser, filter_locations(is_known), filter_locations(is_unknown)


def get_lag_and_ili(issue, epiweek, num_ili, num_patients):
    """
    Compute and return reporting lag and percent ILI from imputed ILINet data.
    """
    lag = delta_epiweeks(epiweek, issue)
    ili = 100.0 * (0 if num_patients == 0 else num_ili / num_patients)
    return lag, ili


def impute_missing_values(database, test_mode=False):
    """
    Determine whether values are missing for any states and territories. If so,
    impute them and store them in the database.
    """

    # database connection
    database.connect()
    rows1 = database.count_rows()
    print(f"rows before: {int(rows1)}")

    # iterate over missing epiweeks
    missing_rows = database.find_missing_rows()
    print(f"missing data for {len(missing_rows)} epiweeks")
    for issue, epiweek in missing_rows:
        print(f"i={int(issue)} e={int(epiweek)}")

        # get known values from table `fluview`
        known_values = database.get_known_values(issue, epiweek)

        # Unlike most other state-level data, which typically begins publicly on
        # 2010w40, data for PR begins on 2013w40. Before this, there are no reports
        # for PR. Here we assume that no report is equivalent to a report of all
        # zeros (number of ILI, patients, and providers). That's mostly true, with
        # the notable exception of wILI, but that's not relevant here. By assuming
        # that PR reports zero on those weeks, it's possible to impute values for
        # VI, which are otherwise not reported until 2015w40.
        assume_pr_zero = epiweek < 201340 and "pr" not in known_values
        if assume_pr_zero:
            known_values["pr"] = (0, 0, 0)

        # get the imputation matrix and lists of known and unknown locations
        F, known, unknown = get_fusion_parameters(known_values.keys())

        # finally, impute the missing values
        z = np.array([known_values[k] for k in known])
        y = np.dot(F, z)

        # possibly also record the assumptions made for PR
        if assume_pr_zero:
            unknown.append("pr")
            y = np.vstack((y, [known_values["pr"]]))

        # add lag and percent ILI to the data for each imputed location
        imputed_values = {}
        for loc, values in zip(unknown, y):
            n_ili, n_pat, n_prov = map(int, np.rint(values))
            lag, ili = get_lag_and_ili(issue, epiweek, n_ili, n_pat)
            imputed_values[loc] = (lag, n_ili, n_pat, n_prov, ili)
            print(f" {loc}: {str(imputed_values[loc])}")

        # save all imputed values in table `fluview_imputed`
        database.add_imputed_values(issue, epiweek, imputed_values)

    # database cleanup
    rows2 = database.count_rows()
    print(f"rows after: {int(rows2)} (added {int(rows2 - rows1)})")
    commit = not test_mode
    database.close(commit)


def get_argument_parser():
    """Set up command line arguments and usage."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="do dry run only, do not update the database"
    )
    return parser


def main():
    """Run this script from the command line."""
    args = get_argument_parser().parse_args()
    impute_missing_values(Database(), test_mode=args.test)


if __name__ == "__main__":
    main()
