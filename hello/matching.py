import os
import psycopg2
import logging
import json
from psycopg2.extras import RealDictCursor, DictCursor

DATABASE_URL = os.environ['DATABASE_URL']

logger = logging.getLogger(__name__)


def db__get_next_leetcode_team_invite(timezone):
    """
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, link, team_name FROM leetcode_team_invites WHERE sent = FALSE AND timezone = %s ORDER BY created_on;", (timezone,))
    query_result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if query_result:
        return query_result
    return {}

def db__leetcode_invite_sent_confirmation(invite_id):
    """
    update sent: t
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE leetcode_team_invites SET sent = TRUE WHERE id = %s", (invite_id, ))
    conn.commit()
    cur.close()
    conn.close()

def db__add_leetcode_team_invite(
        link,
        team_name,
        timezone
        ):
    """
            db__add_leetcode_team_invite(
                    "https://t.me/joinchat/NLhKahTCOb0kU7dsCtwB_g",
                    "Leetcode Team 506",
                    timezone
            )
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    logger.info("inserting team invite with args:")
    insert_args = (link, team_name, timezone)
    logger.info(insert_args)
    cur.execute("INSERT INTO leetcode_team_invites (link, team_name, timezone) VALUES (%s, %s, %s)",
            insert_args)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("CLI application to insert invites by hand in DB")
    while True:
        print("timezone(pst,ist,est,gmt,gmt+8)=")
        timezone=input()
        print("link=")
        link=input()
        print("team_name=")
        team_name=input()
        print("number of invites (int)=")
        number = int(input())
        for _ in range(number):
            db__add_leetcode_team_invite(
                    link,
                    team_name,
                    timezone
            )


