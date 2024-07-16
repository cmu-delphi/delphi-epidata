from collections import namedtuple
from smtplib import SMTP

import delphi.operations.secrets as secrets
import mysql.connector
from delphi.epidata.server._config import API_KEY_REGISTRATION_FORM_LINK_LOCAL
from delphi.epidata.server._common import send_email

ApiUserRecord = namedtuple("APIUserRecord", ("api_key", "email", "date_diff"))


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


def main():
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(database="epidata", user=u, password=p, host=secrets.db.host)
    cur = cnx.cursor()
    outdated_keys_list = get_old_keys(cur)
    for item in outdated_keys_list:
        if item.date_diff == 5:
            send_email(
                to_addr=item.email,
                subject="API Key will be expired soon",
                message=f"Hi! \n Your API Key: {item.api_key}, is going to be expired due to inactivity.",
            )
        else:
            remove_outdated_key(cur, item.api_key)
            send_email(
                to_addr=item.email,
                subject="Your API Key was expired",
                message=f"Hi! \n Your API Key: {item.api_key}, was removed due to inactivity. To get new one, please use registration form ({API_KEY_REGISTRATION_FORM_LINK_LOCAL}) or contact us.""
            )
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
