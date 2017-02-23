"""
===============
=== Purpose ===
===============

Checks the `fluview` table to see if new data is available. If so, it queues
the automation flow 'New FluView Available'. This will cause, at least:
  - impute state ILI
  - predict next issue wILI (sar3 and arch)
  - score the last epicast round
  - send epicast email notifications


=================
=== Changelog ===
=================

2017-02-22
  * use secrets
2016-04-07
  + Initial version
"""

# standard library
import argparse
# third party
import mysql.connector
# first party
import secrets

if __name__ == '__main__':
  # Args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('-t', '--test', action='store_const', const=True, default=False, help="do dry run only, don't update the database")
  args = parser.parse_args()

  # connect
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  # get the last known issue from the automation table `variables`
  cur.execute('SELECT `value` FROM automation.`variables` WHERE `name` = %s', ('most_recent_issue',))
  for (issue1,) in cur:
    issue1 = int(issue1)
  print('last known issue:', issue1)
  # get the most recent issue from the epidata table `fluview`
  cur.execute('SELECT max(`issue`) FROM `fluview`')
  for (issue2,) in cur:
    issue2 = int(issue2)
  print('most recent issue:', issue2)

  if issue2 > issue1:
    print('new data is available!')
    if args.test:
      print('test mode - not making any changes')
    else:
      # update the variable
      cur.execute('UPDATE automation.`variables` SET `value` = %s WHERE `name` = %s', (issue2, 'most_recent_issue'))
      # queue the 'New FluView Available' flow
      cur.execute('CALL automation.RunStep(36)')
  elif issue2 < issue2:
    raise Exception('most recent issue is older than the last known issue')

  # cleanup
  cnx.commit()
  cur.close()
  cnx.close()
