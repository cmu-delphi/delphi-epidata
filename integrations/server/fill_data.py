"""Integration tests for the `covidcast` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests
import random


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

def fill_db():
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast')
    cnx.commit()
    cur.close()

    cur = cnx.cursor()

    geo_values = 1000
    time_values = 1000

    for geo_value in range(geo_values):
      """
      id, source, signal, time_type, geo_type, 
      time_value, geo_value,
      value_updated_timestamp, value, stderr, sample_size, 
      direction_updated_timestamp, direction, issue, lag, is_latest_issue, is_wip
      """
      arr = [f"""(0, 'src', 'sig', 'day', 'county',
      {time_value}, '{geo_value}', 0, {random.randint(0, 100)}, 2, 12, 0, 1, 20200413, 0, True, False)""" for time_value in range(time_values)]
      cur.execute(f"insert into covidcast values {','.join(arr)}")
      cnx.commit()

fill_db()