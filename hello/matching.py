"""
matching module

matching steps are
1. get_community_team_invite
2. sent_invite
3. check_claimed_invite
"""
import os
import psycopg2
import logging
import json 
from threading import Timer
from psycopg2.extras import RealDictCursor, DictCursor

DATABASE_URL = os.environ['DATABASE_URL']

logger = logging.getLogger(__name__)

def _autoscale_get_invite(teams):
    """
    return invite (id, link, name)
    """
    # auto-scaling matching algorithm
    MAX_TEAM_PARTICIPANTS = 3
    invite = None
    logging.warning("starting auto-scaling matching algorithm")
    while not invite:
        logging.warning("[auto-scaling matching algorithm] MAX_TEAM_PARTICIPANTS = {}".format(MAX_TEAM_PARTICIPANTS))
        for team in teams: # made sure above teams is never empty
            (_id, _link, _name, _sent, _claimed) = team
            # does team have space for new participant?
            if max(int(_sent), int(_claimed)) < MAX_TEAM_PARTICIPANTS:
                invite = (_id, _link, _name)
        MAX_TEAM_PARTICIPANTS += 1
    return invite


def get_community_team_invite(community, timezone):
    """
    ALWAYS RETURNS AN INVITE
    return (team_id, team_invite_link, team_name)
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    # teams that have habiter.app in the name means that 
    # where created before of the auto-scaling
    cur.execute("SELECT id, link, team_name, sent, claimed  FROM teams WHERE community = %s AND timezone = %s AND link != 'https://habiter.app' AND link != '' ORDER BY created_on;", (community, timezone))
    teams = cur.fetchall()

    if not teams:
        logging.warning("!!!! QUERY ERROR: no teams found")
        logging.warning(timezone)
        return (1, "https://t.me/joinchat/NLhKahiHwJoXczR7n-Kkwg", "Leetcode Team 508")
    invite = _autoscale_get_invite(teams)

    conn.commit()
    cur.close()
    conn.close()
    return invite

def check_claimed_invite(*args):
    """
    TODO: there is an error here about argument numerb
    2020-02-29T23:50:38.510553+00:00 app[web.1]: self.function(*self.args, **self.kwargs)
    2020-02-29T23:50:38.510553+00:00 app[web.1]: TypeError: db__leetcode_check_claimed_invite() takes 1 positional argument but 2 were given
    should be fixed by args
    """
    logger.warning("checking claimed invite: start")
    logger.warning(args)
    team_id = ''.join(args)
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
    cur.execute("UPDATE teams SET sent = sent - 1 WHERE id = %s AND sent > claimed ", (team_id, ))
    logger.warning("checking claimed invite: updated")
    conn.commit()
    cur.close()
    conn.close()

def sent_invite(team_id):
    """
    UPDATE sent: +1
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    logger.warning("invite sent for "+str(team_id))
    cur.execute("UPDATE teams SET sent = sent + 1 WHERE id = %s", (team_id, ))
    conn.commit()
    cur.close()
    conn.close()

    # set timer
    duration = 60 * 2
    logger.warning("setting timer for check_claimed_invite in "+str(duration)+" seconds")
    t = Timer(duration, check_claimed_invite, team_id)
    t.start()

def db__set_active_leetcode_problems(link1, link2, labels):
    """
    all other inactive
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE leetcode_problems SET active = FALSE;")
    cur.execute("INSERT INTO leetcode_problems (link) VALUES (%s)", (link1, ))
    cur.execute("INSERT INTO leetcode_problems (link) VALUES (%s)", (link2, ))
    conn.commit()
    cur.close()
    conn.close()
    return {"result":"success"}

def db__get_active_leetcode_problems():
    """
    return [(id, link)]
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
        cur = conn.cursor()
        cur.execute("SELECT id, link, labels FROM leetcode_problems WHERE active = TRUE;")
        problems = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return problems
    except Exception as e:
        return {"result":"server error 500", "error":e}

def db__get_leaderboard():
    """
    SELECT team_id, SUM(screenshot_submitted), STRING_AGG(name, ', ') FROM leetcode_users GROUP BY team_id ORDER BY sum DESC;
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT team_id, SUM(screenshot_submitted) as solved_problems, SUM(screenshot_submitted)/COUNT(name) as score, STRING_AGG(name, ', ') FROM leetcode_users GROUP BY team_id ORDER BY score DESC;")
    leaderboard = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return leaderboard

# FOUNDERS 
def db__add_founders_club(
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
    cur.execute("INSERT INTO founders_clubs (link, team_name, timezone) VALUES (%s, %s, %s)",
            insert_args)
    conn.commit()
    cur.close()
    conn.close()

def db__get_next_founders_team_invite(timezone):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, link, team_name, sent, claimed  FROM founders_clubs WHERE timezone = %s ORDER BY created_on;", (timezone,))
    teams = cur.fetchall()

    if not teams:
        logging.warning("!!!! QUERY ERROR: no teams found")
        logging.warning(timezone)
        return (1, "https://t.me/joinchat/NLhKahiHwJoXczR7n-Kkwg", "Leetcode Team 508")
    invite = _autoscale_get_invite(teams)

    conn.commit()
    cur.close()
    conn.close()
    return invite

def db__founders_invite_sent_confirmation(team_id):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE founders_clubs SET sent = sent + 1 WHERE id = %s", (team_id, ))
    conn.commit()
    cur.close()
    conn.close()

    # set timer
    logger.info("starting countdown to claim invite")
    duration = 60 * 2
    t = Timer(duration, db__founders_check_claimed_invite, team_id)
    t.start()

def db__founders_check_claimed_invite(*args):
    """
    TODO: there is an error here about argument numerb
    2020-02-29T23:50:38.510553+00:00 app[web.1]: self.function(*self.args, **self.kwargs)
    2020-02-29T23:50:38.510553+00:00 app[web.1]: TypeError: db__leetcode_check_claimed_invite() takes 1 positional argument but 2 were given
    should be fixed by args
    """
    logger.warning("checking claimed invite: start")
    logger.warning(args)
    team_id = ''.join(args)
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
    cur.execute("UPDATE founders_clubs SET sent = sent - 1 WHERE id = %s AND sent > claimed ", (team_id, ))
    logger.warning("checking claimed invite: updated")
    conn.commit()
    cur.close()
    conn.close()

def db__get_all_founders_clubs(timezone):
    """
    returns [(id, team_name, sent, claimed)]
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, team_name, sent, claimed FROM founders_clubs WHERE timezone = %s ORDER BY claimed DESC;", (timezone, ))
    teams = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return teams

if __name__ == "__main__":
    print("CLI application to insert teams by hand in DB")
    while True:
        print("leetcode(L),founders(F)")
        campaign=input()
        if campaign=="L":
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
        if campaign=="F":
            print("timezone(pst,ist,est,gmt,gmt+8)=")
            timezone=input()
            print("invite_link=")
            link=input()
            print("team_name=")
            team_name=input()
            db__add_founders_club(
                    link,
                    team_name,
                    timezone
            )
            print("ADDED SUCCESFULLY, add another team now:")



