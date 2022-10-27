from delphi.epidata.acquisition.covid_hosp.auto_update_schema import \
    split_sql, \
    db_to_columns, \
    annotate_columns_using_ddl, \
    Column
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
import pytest

@pytest.fixture
def split_sql_given():
    return """
USE covidcast;

/*
xyzzy
*/

CREATE TABLE `kitchen` (
`id` INT NOT NULL AUTO_INCREMENT,
sink VARCHAR(8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
quux
| bar |
*/

CREATE TABLE `maze` (
`turn` INT NOT NULL AUTO_INCREMENT,
`direction` CHAR(2) NOT NULL,
-- test comment
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

@pytest.fixture
def split_sql_expected():
    # x[1:] to drop the initial newline (included for readability)
    return list(x[1:] for x in [
        """
USE covidcast""",
        """
xyzzy""",
        """
CREATE TABLE `kitchen` (
`id` INT NOT NULL AUTO_INCREMENT,
sink VARCHAR(8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8""",
        """
quux
| bar |""",
        """
CREATE TABLE `maze` (
`turn` INT NOT NULL AUTO_INCREMENT,
`direction` CHAR(2) NOT NULL,
-- test comment
) ENGINE=InnoDB DEFAULT CHARSET=utf8"""
    ])


def test_split_sql(split_sql_given, split_sql_expected):
    assert split_sql(split_sql_given) == split_sql_expected



@pytest.fixture
def columns_as_Database():
    class Database:
        ORDERED_CSV_COLUMNS = [
            ("int_csv", "int_sql", int),
            ("str_csv", "str_sql", str),
            ("float_csv", "float_sql", float),
            ("date_csv", "date_sql", Utils.int_from_date)
        ]
    return Database

@pytest.fixture
def columns_as_Columns():
    initializers = [int, str, float, Utils.int_from_date]
    return {
        f"{t}_csv": Column(
            csv_name=f"{t}_csv",
            sql_name=f"{t}_sql",
            py_type=initializers[i]
        ) for i, t in enumerate(["int", "str", "float", "date"])
    }


def _match_fields(actual, expected, *fields):
    for fi in fields:
        assert getattr(actual, fi) == getattr(expected, fi)


def test_db_to_columns(columns_as_Database, columns_as_Columns):
    actual = db_to_columns(columns_as_Database)
    for ki in set(list(actual) + list(columns_as_Columns)):
        assert ki in actual
        assert ki in columns_as_Columns
        _match_fields(
            actual[ki],
            columns_as_Columns[ki],
            *"csv_name sql_name py_type".split()
        )

@pytest.fixture
def columns_as_SQL():
    return """
CREATE TABLE `table1` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `int_sql` INT NOT NULL,
  `str_sql` VARCHAR(8) NOT NULL,
  `float_sql` DOUBLE,
  `date_sql` INT(8) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `str_by_date` (`str_sql`, `date_sql`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

@pytest.fixture
def annotated_columns(columns_as_Columns):
    def update(c, sql_type, sql_type_size=None, required=False, extra=None):
        c.sql_type = sql_type
        if sql_type_size is not None:
            c.sql_type_size = sql_type_size
        c.required = required
        if extra:
            c.sql_extra = extra
    update(columns_as_Columns['int_csv'], "int", required=True)
    update(columns_as_Columns['str_csv'], "varchar", 8, True)
    update(columns_as_Columns['float_csv'], "double")
    update(columns_as_Columns['date_csv'], "int", 8, True)
    return columns_as_Columns

def test_annotate_columns_using_ddl(columns_as_Columns, columns_as_SQL, annotated_columns):
    remapped = annotate_columns_using_ddl(
        {'table1': [columns_as_Columns]},
        columns_as_SQL
    )
    assert 'id' not in annotated_columns
    assert 'id' in remapped['table1'][0]
    for ki in annotated_columns:
        _match_fields(
            columns_as_Columns[ki],
            annotated_columns[ki],
            *"sql_type sql_type_size required".split()
        )

