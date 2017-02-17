'''
===============
=== Purpose ===
===============

Stores flu-related search volume using private Google APIs (Trends and Health).
In theory, this data could be used to reconstruct Google Flu Trends.

The program checks (up to) all U.S. states, DC, and the entire US (52) over the
following inclusive epiweek range:
  From: 4 weeks prior to the most recently stored date
  To: the actual week at runtime

See: google_health_trends.py


=======================
=== Data Dictionary ===
=======================

`ght` is the table where Google health trends metadata is stored.
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| query    | varchar(64) | NO   | MUL | NULL    |                |
| location | varchar(8)  | NO   | MUL | NULL    |                |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| value    | float       | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
query: a search string or topic ID (see https://www.freebase.com/)
location: two-letter U.S. state abbreviation, or 'US' for entire US
epiweek: the epiweek during which the queries were executed
value: relative search volume; the exact definition is still unclear


=================
=== Changelog ===
=================

2017-02-16:
  * use secrets
2016-06-20:
  * updated list of terms (matching 2010-04-19 through 2015-05-05)
2016-06-13:
  * don't give up so easily (now 5 retries)
2016-06-10:
  + automatic retry on API failure, up to 3 retries
  + ability to update all terms in a single run
  * store values of zero
  * consolidate reports of missing values
2016-04-14:
  + first and last epiweek override
  * don't wrap terms in quotation marks
  * allow multiple locations
2016-01-29:
  + command line arguments for updating specific locations/terms
  - moved GHT class to google_health_trends.py
2015-12-04
  * not including quotes when storing to database
2015-12-03
  * fixed multiple-word queries (surround with quotes)
2015-12-01
  * Original version
'''

# built-in
import argparse
import time
# external
import mysql.connector
from apiclient.discovery import build
# local
from epidate import EpiDate
import epiweek as flu
from google_health_trends import GHT
import secrets


# secret key for accessing Google's health trends APIs
# see: https://console.developers.google.com/apis/credentials?project=delphi-epi-trends
API_KEY = secrets.googletrends.apikey

# search strings and topics that are most highly correlated with wILI between
# 2010-04-19 and 2015-05-05
# see: https://www.google.com/trends/correlate
TERMS = [
  '/m/0cycc',
  'influenza type a',
  'flu duration',
  'flu fever',
  'treating flu',
  'fever flu',
  'flu recovery',
  'braun thermoscan',
  'oscillococcinum',
  'treating the flu',
  'cold or flu',
  'flu versus cold',
  'flu remedies',
  'contagious flu',
  'type a influenza',
  'flu or cold',
  'duration of flu',
  'cold versus flu',
  'flu cough',
  'flu headache',
  'thermoscan',
  'influenza incubation period',
  'flu lasts',
  'length of flu',
  'flu stomach',
  'cold vs flu',
  'flu and fever',
  'getting over the flu',
  'influenza a',
  'treatment for flu',
  'flu length',
  'treatment for the flu',
  'influenza symptoms',
  'over the counter flu',
  'flu complications',
  'cold and flu symptoms',
  'influenza incubation',
  'treatment of flu',
  'human temperature',
  'low body',
  'flu contagious',
  'robitussin ac',
  'flu how long',
  'ear thermometer',
  'flu contagious period',
  'treat flu',
  'cough flu',
  'low body temperature',
  'expectorant',
  'flu and cold',
  'rapid flu',
  'flu vs. cold',
  'how to treat the flu',
  'how long does the flu last?',
  'viral pneumonia',
  'flu in kids',
  'type a flu',
  'influenza treatment',
  'fighting the flu',
  'flu relief',
  'treat the flu',
  'flu medicine',
  'dangerous fever',
  'what is influenza',
  'tussin',
  'low body temp',
  'flu care',
  'flu in infants',
  'flu dizziness',
  'feed a fever',
  'flu vs cold',
  'flu vomiting',
  'bacterial pneumonia',
  'flu activity',
  'flu chills',
  'anas barbariae',
  'flu germs',
  'tylenol cold',
  'how to get over the flu',
  'flu in children',
  'influenza a and b',
  'duration of the flu',
  'cold symptoms',
  'flu report',
  'rapid flu test',
  'flu relapse',
  'get over the flu',
  'flu during pregnancy',
  'flu recovery time',
  'cure for flu',
  'tamiflu and breastfeeding',
  'flu chest pain',
  'flu treatment',
  'flu nausea',
  'remedies for the flu',
  'tamiflu in pregnancy',
  'side effects of tamiflu',
  'how to treat flu',
  'viral bronchitis',
  'flu how long contagious',
  'flu remedy',
]

# a list of all US states, including DC and the US as a whole
LOCATIONS = [
  'US',
  'AL',
  'AK',
  'AZ',
  'AR',
  'CA',
  'CO',
  'CT',
  'DC',
  'DE',
  'FL',
  'GA',
  'HI',
  'ID',
  'IL',
  'IN',
  'IA',
  'KS',
  'KY',
  'LA',
  'ME',
  'MD',
  'MA',
  'MI',
  'MN',
  'MS',
  'MO',
  'MT',
  'NE',
  'NV',
  'NH',
  'NJ',
  'NM',
  'NY',
  'NC',
  'ND',
  'OH',
  'OK',
  'OR',
  'PA',
  'RI',
  'SC',
  'SD',
  'TN',
  'TX',
  'UT',
  'VT',
  'VA',
  'WA',
  'WV',
  'WI',
  'WY',
]


def update(locations, terms, first=None, last=None):
  # connect to the database
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  def get_num_rows():
    cur.execute('SELECT count(1) `num` FROM `ght`')
    for (num,) in cur:
      pass
    return num

  # check from 4 weeks preceeding the last week with data through this week
  cur.execute('SELECT max(`epiweek`) `ew0`, yearweek(now(), 6) `ew1` FROM `ght`')
  for (ew0, ew1) in cur:
    ew0 = 200401 if ew0 is None else flu.add_epiweeks(ew0, -4)
  ew0 = ew0 if first is None else first
  ew1 = ew1 if last is None else last
  print('Checking epiweeks between %d and %d...' % (ew0, ew1))

  # keep track of how many rows were added
  rows_before = get_num_rows()

  # check Google Trends for new and/or revised data
  sql = '''
    INSERT INTO
      `ght` (`query`, `location`, `epiweek`, `value`)
    VALUES
      (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      `value` = %s
  '''
  total_rows = 0
  ght = GHT(API_KEY)
  for term in terms:
    print(' [%s] using term' % term)
    for location in locations:
      try:
        #term2 = ('"%s"' % term) if ' ' in term else term
        term2 = term
        attempt = 0
        while True:
          attempt += 1
          try:
            result = ght.get_data(ew0, ew1, location, term2)
            break
          except Exception as ex:
            if attempt >= 5:
              raise ex
            else:
              delay = 2 ** attempt
              print(' [%s|%s] caught exception (will retry in %ds):' % (term, location, delay), ex)
              time.sleep(delay)
        values = [p['value'] for p in result['data']['lines'][0]['points']]
        ew = result['start_week']
        num_missing = 0
        for v in values:
          sql_data = (term, location, ew, v, v)
          cur.execute(sql, sql_data)
          total_rows += 1
          if v == 0:
            num_missing += 1
            #print(' [%s|%s|%d] missing value' % (term, location, ew))
          ew = flu.add_epiweeks(ew, 1)
        if num_missing > 0:
          print(' [%s|%s] missing %d/%d value(s)' % (term, location, num_missing, len(values)))
      except Exception as ex:
        print(' [%s|%s] caught exception (will NOT retry):' % (term, location), ex)

  # keep track of how many rows were added
  rows_after = get_num_rows()
  print('Inserted %d/%d row(s)'%(rows_after - rows_before, total_rows))

  # cleanup
  cur.close()
  cnx.commit()
  cnx.close()


def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('location', action='store', type=str, default=None, help='location(s) (ex: all; US; TX; CA,LA,WY)')
  parser.add_argument('term', action='store', type=str, default=None, help='term/query/topic (ex: all; /m/0cycc; "flu fever")')
  parser.add_argument('--first', '-f', default=None, type=int, help='first epiweek override')
  parser.add_argument('--last', '-l', default=None, type=int, help='last epiweek override')
  args = parser.parse_args()

  # sanity check
  first, last = args.first, args.last
  if first is not None:
    flu.check_epiweek(first)
  if last is not None:
    flu.check_epiweek(last)
  if first is not None and last is not None and first > last:
    raise Exception('epiweeks in the wrong order')

  # decide what to update
  if args.location.lower() == 'all':
    locations = LOCATIONS
  else:
    locations = args.location.upper().split(',')
  if args.term.lower() == 'all':
    terms = TERMS
  else:
    terms = [args.term]

  # run the update
  update(locations, terms, first, last)


if __name__ == '__main__':
  main()
