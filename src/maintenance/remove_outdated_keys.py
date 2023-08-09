from collections import namedtuple

import delphi.operations.secrets as secrets
import mysql.connector
from delphi.epidata.server._config import API_KEY_REGISTRATION_FORM_LINK_LOCAL
from delphi.epidata.server._common import send_email

ApiUserRecord = namedtuple("APIUserRecord", ("api_key", "email", "date_diff"))

ALERT_EMAIL_MESSAGE = """Hi! \n Your API Key: {} is going to be removed due to inactivity.
To renew it, pelase use it within one month from now."""
DELETED_EMAIL_MESSAGE = """Hi! \n Your API Key: {} was removed due to inactivity.
To get new one, please use registration form ({}) or contact us."""


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
            send_email(item.email, "Your API Key will be expired soon.", ALERT_EMAIL_MESSAGE.format(item.api_key))
        else:
            remove_outdated_key(cur, item.api_key)
            send_email(
                item.email,
                f"Your API Key was deleted.",
                DELETED_EMAIL_MESSAGE.format(item.api_key, API_KEY_REGISTRATION_FORM_LINK_LOCAL),
            )
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
