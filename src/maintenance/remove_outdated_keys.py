from collections import namedtuple
from smtplib import SMTP

import delphi.operations.secrets as secrets
import mysql.connector
from delphi.epidata.server._config import API_KEY_REGISTRATION_FORM_LINK_LOCAL

API_USER_RECORD = namedtuple("APIUser", ("api_key", "email", "date_diff"))

SMTP_HOST = "relay.andrew.cmu.edu"
SMTP_PORT = 25

EMAIL_SUBJECT = "Your API Key was deleted."
EMAIL_FROM = "noreply@andrew.cmu.edu"
EMAIL_MESSAGE = f"""Hi! \n Your API Key was removed due to inactivity.
To get new one, please use registration form ({API_KEY_REGISTRATION_FORM_LINK_LOCAL}) or contact us."""


def get_outdated_keys(cur):
    cur.execute(
        """
            SELECT
                diff.api_key,
                diff.email,
                diff.date_diff
            FROM (
                SELECT
                    api_key,
                    email,
                    created,
                    last_time_used,
                    ABS(TIMESTAMPDIFF(MONTH, last_time_used, created)) as date_diff
                FROM api_user
            ) diff
            WHERE diff.date_diff >= 5;

        """
    )
    outdated_keys = cur.fetchall()
    return outdated_keys


def remove_outdated_key(cur, api_key):
    cur.execute(
        f"""
            DELETE FROM api_user WHERE api_key = "{api_key}"
        """
    )


def send_notification(to_addr):
    BODY = "\r\n".join((f"FROM: {EMAIL_FROM}", f"TO: {to_addr}", f"Subject: {EMAIL_SUBJECT}", "", EMAIL_MESSAGE))
    smtp_server = SMTP(host=SMTP_HOST, port=SMTP_PORT)
    smtp_server.sendmail(EMAIL_FROM, to_addr, BODY)


def main():
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(database="epidata", user=u, password=p, host=secrets.db.host)
    cur = cnx.cursor()
    outdated_keys_list = [API_USER_RECORD(*item) for item in get_outdated_keys(cur)]
    for item in outdated_keys_list:
        if item.date_diff == 5:
            send_notification(item.email)
        else:
            remove_outdated_key(cur, item.api_key)
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
