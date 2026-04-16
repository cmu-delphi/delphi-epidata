import logging
import os
from datetime import datetime as dtime

import delphi.operations.secrets as secrets
import mysql.connector
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "delphi_redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
LAST_USED_KEY_PATTERN = "*LAST_USED*"

logger = logging.getLogger(__name__)


def main():
    logger.info("Connecting to Redis at %s", REDIS_HOST)
    redis_cli = redis.Redis(
        host=REDIS_HOST, password=REDIS_PASSWORD, decode_responses=True
    )
    u, p = secrets.db.epi
    logger.info("Connecting to MySQL at %s", secrets.db.host)
    cnx = mysql.connector.connect(
        database="epidata", user=u, password=p, host=secrets.db.host
    )
    cur = cnx.cursor()

    redis_keys = redis_cli.keys(pattern=LAST_USED_KEY_PATTERN)
    logger.info("Found %d LAST_USED keys in Redis", len(redis_keys))
    for key in redis_keys:
        api_key, last_time_used = (
            str(key).split("/")[1],
            dtime.strptime(str(redis_cli.get(key)), "%Y-%m-%d").date(),
        )
        cur.execute(
            f"""
            UPDATE
                api_user
            SET last_time_used = "{last_time_used}"
            WHERE api_key = "{api_key}" AND (last_time_used < "{last_time_used}" OR last_time_used IS NULL)
        """
        )
    logger.info("Flushed %d Redis key last usage to MySQL", len(redis_keys))

    # migrate any keys not already in redis over
    redis_key_set = {str(key).split("/")[1] for key in redis_keys}
    cur.execute("SELECT api_key, last_time_used FROM api_user")
    migrated = 0
    for api_key, last_time_used in cur.fetchall():
        if api_key not in redis_key_set:
            date_str = (
                dtime.strftime(last_time_used, "%Y-%m-%d")
                if last_time_used
                else dtime.strftime(dtime.now(), "%Y-%m-%d")
            )
            redis_cli.set(f"LAST_USED/{api_key}", date_str)
            migrated += 1
    logger.info("Migrated %d keys from MySQL to Redis", migrated)

    cur.close()
    cnx.commit()
    cnx.close()
    logger.info("Done")


if __name__ == "__main__":
    main()
