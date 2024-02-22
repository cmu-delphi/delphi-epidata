from collections import namedtuple
from smtplib import SMTP

import delphi.operations.secrets as secrets
import MySQLdb
from delphi.epidata.server._config import API_KEY_REGISTRATION_FORM_LINK_LOCAL

ApiUserRecord = namedtuple("APIUserRecord", ("api_key", "email", "date_diff"))

SMTP_HOST = "relay.andrew.cmu.edu"
SMTP_PORT = 25

EMAIL_SUBJECT = "Your API Key was deleted."
EMAIL_FROM = "noreply@andrew.cmu.edu"
ALERT_EMAIL_MESSAGE = f"""Hi! \n Your API Key is going to be removed due to inactivity.
To renew it, pelase use it within one month from now."""
DELETED_EMAIL_MESSAGE = f"""Hi! \n Your API Key was removed due to inactivity.
To get new one, please use registration form ({API_KEY_REGISTRATION_FORM_LINK_LOCAL}) or contact us."""


def get_old_keys(cur):
    cur.execute(
        """
        SELECT
            api_key,
            email,
            TIMESTAMPDIFF(MONTH, last_time_used, NOW()) AS date_diff
        FROM api_user
        HAVING date_diff >= 5;
        """
    )
    outdated_keys = cur.fetchall()
    return [ApiUserRecord(*item) for item in outdated_keys]


def remove_outdated_key(cur, api_key):
    cur.execute(
        f"""
            DELETE FROM api_user WHERE api_key = "{api_key}"
        """
    )


def send_notification(to_addr, alert=True):
    message = ALERT_EMAIL_MESSAGE if alert else DELETED_EMAIL_MESSAGE
    BODY = "\r\n".join((f"FROM: {EMAIL_FROM}", f"TO: {to_addr}", f"Subject: {EMAIL_SUBJECT}", "", message))
    smtp_server = SMTP(host=SMTP_HOST, port=SMTP_PORT)
    smtp_server.starttls()
    smtp_server.sendmail(EMAIL_FROM, to_addr, BODY)


def main():
    u, p = secrets.db.epi
    cnx = MySQLdb.connect(database="epidata", user=u, password=p, host=secrets.db.host)
    cur = cnx.cursor()
    outdated_keys_list = get_old_keys(cur)
    for item in outdated_keys_list:
        if item.date_diff == 5:
            send_notification(item.email)
        else:
            remove_outdated_key(cur, item.api_key)
            send_notification(item.email, alert=False)
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
