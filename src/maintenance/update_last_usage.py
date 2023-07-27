import os
from datetime import datetime as dtime

import delphi.operations.secrets as secrets
import mysql.connector
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "delphi_redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "1234")
LAST_USED_KEY_PATTERN = "*LAST_USED*"


def main():
    redis_cli = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD, decode_responses=True)
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(database="epidata", user=u, password=p, host=secrets.db.host)
    cur = cnx.cursor()

    redis_keys = redis_cli.keys(pattern=LAST_USED_KEY_PATTERN)
    today_date = dtime.today().date()
    for key in redis_keys:
        api_key, last_time_used = str(key).split("/")[1], dtime.strptime(str(redis_cli.get(key)), "%Y-%m-%d").date()
        if last_time_used < today_date:
            redis_cli.delete(key)
            continue
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
