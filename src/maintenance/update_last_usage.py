import os
from datetime import datetime as dtime

import delphi.operations.secrets as secrets
import mysql.connector
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "delphi_redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "1234")
LAST_USED_KEY_PATTERN = "*LAST_USED*"


def redis_get_last_time_used(redis_cli):
    keys = redis_cli.keys(pattern=LAST_USED_KEY_PATTERN)
    key_val_pairs = {
        str(key).split("/")[1]: dtime.strptime(str(redis_cli.get(key)), "%Y-%m-%d").date() for key in keys
    }
    return key_val_pairs


def main():
    redis_cli = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD, decode_responses=True)
    key_val_pairs = redis_get_last_time_used(redis_cli, LAST_USED_KEY_PATTERN)
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(database="epidata", user=u, password=p, host=secrets.db.host)
    cur = cnx.cursor()
    for api_key, last_time_used in key_val_pairs.items():
        cur.execute(
            f"""
            UPDATE
                api_user
            SET last_time_used = "{last_time_used}"
            WHERE api_key = "{api_key}" AND (last_time_used < "{last_time_used}" OR last_time_used IS NULL)
        """
        )
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
