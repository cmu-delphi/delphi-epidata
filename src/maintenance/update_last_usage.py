import os
from datetime import datetime as dtime

import delphi.operations.secrets as secrets
import mysql.connector
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "delphi_redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "1234")
LAST_USED_KEY_PATTERN = "*LAST_USED*"


def redis_get_last_time_used(redis_cli, pattern: str):
    keys = redis_cli.keys(pattern=pattern)
    key_val_pairs = {
        str(key).split("/")[1]: dtime.strptime(str(redis_cli.get(key)), "%Y-%m-%d").date() for key in keys
    }
    return key_val_pairs


def db_get_last_time_used(api_key: str, cur):
    cur.execute(
        f"""
        SELECT
            last_time_used
        FROM api_user
        WHERE api_key = "{api_key}"
        LIMIT 1
        """
    )
    last_time_used = cur.fetchone()
    return last_time_used[0]


def main():
    redis_cli = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD, decode_responses=True)
    key_val_pairs = redis_get_last_time_used(redis_cli, LAST_USED_KEY_PATTERN)
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(database="epidata", user=u, password=p, host=secrets.db.host)
    cur = cnx.cursor()
    for api_key, last_time_used in key_val_pairs.items():
        db_last_time_used = db_get_last_time_used(api_key, cur)
        if db_last_time_used == None or last_time_used > db_last_time_used:
            cur.execute(
                f"""
                UPDATE
                    api_user
                SET last_time_used = "{last_time_used}"
                WHERE api_key = "{api_key}"
            """
            )
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
