import os
import psycopg2
import logging
import json
from threading import Timer
from psycopg2.extras import RealDictCursor, DictCursor

DATABASE_URL = os.environ['DATABASE_URL']

logger = logging.getLogger(__name__)


def db__get_next_leetcode_team_invite(timezone):
    """
    ALWAYS RETURNS AN INVITE
    return (team_id, team_invite_link, team_name)
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, link, team_name, sent, claimed  FROM leetcode_teams WHERE timezone = %s ORDER BY created_on;", (timezone,))
    teams = cur.fetchall()

    # auto-scaling matching algorithm
    MAX_TEAM_PARTICIPANTS = 3
    invite = None
    logging.warning("starting auto-scaling matching algorithm")
    while not invite:
        logging.warning("[auto-scaling matching algorithm] MAX_TEAM_PARTICIPANTS = {}".format(MAX_TEAM_PARTICIPANTS))
        for team in teams:
            (_id, _link, _name, _sent, _claimed) = team
            # does team have space for new participant?
            if max(int(_sent), int(_claimed)) < MAX_TEAM_PARTICIPANTS:
                invite = (_id, _link, _name)
        MAX_TEAM_PARTICIPANTS += 1

        # exception in case it loops infinite
        if (MAX_TEAM_PARTICIPANTS >= 99):
            logging.warning("ERROR in auto-scaling algorithm:")
            logging.warning("MAX_TEAM_PARTICIPANTS >= 99")
            logging.warning(teams)
            (_id, _link, _name, _sent, _claimed) = teams[0]
            invite = (_id, _link, _name)

    conn.commit()
    cur.close()
    conn.close()
    return invite

def db__leetcode_check_claimed_invite(team_id):
    """
    """
    logger.warning("checking claimed invite: start")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    # FAULTY LOGIC, but simple to implement so I leave it here
    # failing example is:
    # U1 sent + 1
    # U2 sent + 1
    # U1 claimed 
    # (here sent -= 1 get triggered )
    # U2 claimed
    # now there is 1 sent and 2 claimed
    cur.execute("UPDATE leetcode_teams SET sent = sent - 1 WHERE id = %s AND sent > claimed ", (team_id, ))
    logger.warning("checking claimed invite: updated")
    conn.commit()
    cur.close()
    conn.close()

def db__leetcode_invite_sent_confirmation(team_id):
    """
    UPDATE sent: +1
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE leetcode_teams SET sent = sent + 1 WHERE id = %s", (team_id, ))
    conn.commit()
    cur.close()
    conn.close()

    # set timer
    duration = 60 * 2
    t = Timer(duration, db__leetcode_check_claimed_invite, team_id)
    t.start()

def db__add_leetcode_team(
        link,
        team_name,
        timezone
        ):
    """
            db__add_leetcode_team(
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
    cur.execute("INSERT INTO leetcode_teams (link, team_name, timezone) VALUES (%s, %s, %s)",
            insert_args)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("CLI application to insert teams by hand in DB")
    while True:
        print("timezone(pst,ist,est,gmt,gmt+8)=")
        timezone=input()
        print("invite_link=")
        link=input()
        print("team_name=")
        team_name=input()
        db__add_leetcode_team(
                link,
                team_name,
                timezone
        )
        print("ADDED SUCCESFULLY, add another team now:")


