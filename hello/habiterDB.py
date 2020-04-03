"""
cross-community database schema API
"""
import os
import psycopg2
import logging
import json 
from threading import Timer
from psycopg2.extras import RealDictCursor, DictCursor

DATABASE_URL = os.environ['DATABASE_URL'] 
logger = logging.getLogger(__name__)

"""
move later to community.CONTENT
"""

def get_communities():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT name, name FROM communities;")
    content = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return content

def get_community_admin(community):
    logger.warning("getting community admin for "+str(community))
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT admin FROM communities WHERE name = %s", (community, ))
    content = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    logger.warning(content)
    return content


def add_community_content_item(link, label, community):
    """
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("INSERT INTO content (link, label, community) VALUES (%s, %s, %s)", (link, label, community))
    conn.commit()
    cur.close()
    conn.close()
    return {"result":"success"}

def _get_community_content(community):
    """
    plain query to community 
    community: "Leetcode"
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, link, label FROM content WHERE community = %s;", (community,))
    content = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return content

def get_community_content_labels(community):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT(label) FROM content WHERE community = %s;", (community,))
    content = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return content

def get_community_content(community):
    """
    like _get_community_content
    but augment with content index information
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, link, label FROM content WHERE community = %s ORDER BY id;", (community,))
    content = cur.fetchall()
    cur.execute("SELECT id, team_name, content_index FROM teams WHERE community = %s;", (community,))
    teams = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    augmented_content = []
    # augment content with content_index information
    for item in content:
        index = item[0]
        teams_on_index = [team[1] for team in teams if team[2] == index]
        augmented_item = list((item)) + [teams_on_index]
        augmented_content.append(augmented_item)
    return augmented_content

"""
move later to commmunity.TEAMS
"""

def get_community_teams(community):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, team_name, sent, claimed, link, label, timezone, session_time, active FROM teams WHERE community = %s ORDER BY team_name DESC;", (community, ))
    teams = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return teams

def get_community_master_team(community):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, team_name, sent, claimed, link, label, timezone, session_time, active FROM teams WHERE community = %s AND label = 'Master' ORDER BY team_name DESC;", (community, ))
    teams = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return teams[0] if teams else None

def get_community_teams_by_timezone(community, timezone):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, team_name, sent, claimed, link, label FROM teams WHERE community = %s AND timezone = %s ORDER BY team_name DESC;", (community, timezone))
    teams = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return teams

def add_community_team(
        community,
        link,
        team_name,
        timezone,
        label):
    """
    TODO: add chat_id
    TODO: make this call automatically from bot, not from UI
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # TODO: how to deal better with this hardcoded stuff?
    session_time = '21:00'
    if timezone == 'est': session_time = '02:00'
    if timezone == 'pst': session_time = '05:00'
    if timezone == 'gmt+8': session_time = '13:00'
    if timezone == 'ist': session_time = '15:30'

    # starting content_index for problems
    content_index = 1
    if label == 'Easy': content_index = 17
    if label == 'Hard': content_index = 25

    logger.info("inserting team invite with args:")
    insert_args = (community, link, team_name, timezone, label, session_time, content_index)
    logger.info(insert_args)
    cur.execute("INSERT INTO teams (community, link, team_name, timezone, label, session_time, content_index) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            insert_args)
    conn.commit()
    cur.close()
    conn.close()



"""
community.USERS
"""
def get_community_users(community):
    """
    query users table, 
    
    # cur.execute("SELECT MIN(user_id),username, COUNT(*) as activity FROM user_actions WHERE community = %s GROUP BY username ORDER BY activity DESC;", (community, ))
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, name, sessions_active_total, sessions_skip_total, sessions_skip_streak, days_active_total, days_since_join FROM users WHERE community = %s", (community, ))
    users = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return users

def user_action_backfill(community):
    """
    """
    if community != 'Leetcode':
        return "backfill supported only for Leetcode at the moment!"

    with open('hello/queries/backfill_users_with_new_users.sql', 'r') as file:
        backfill_users_with_new_users = file.read().replace('\n', ' ')
    with open('hello/queries/backfill_users_with_session_data.sql', 'r') as file:
        backfill_users_with_session_data = file.read().replace('\n', ' ')

    logging.warning("running backfill.. retreived two queries..")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    logging.warning("running first query")
    logging.warning(backfill_users_with_new_users)
    cur.execute(backfill_users_with_new_users)
    logging.warning("running second query")
    logging.warning(backfill_users_with_session_data)
    cur.execute(backfill_users_with_session_data)
    conn.commit()
    cur.close()
    conn.close()


"""
community.BOTS
"""

def get_bot_content_by_community(community):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, description, content FROM bots WHERE community = %s;", (community, ))
    content = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return content

def get_bot_content():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, description, content FROM bots;")
    content = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return content

def edit_bot_content(content_id, new_content):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE bots SET content = %s WHERE id = %s;", (new_content, content_id))
    conn.commit()
    cur.close()
    conn.close()

def edit_bot_content_from_description(
        description, 
        community,
        new_content
        ):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE bots SET content = %s WHERE description = %s AND community = %s;", (new_content, description, community))
    result = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return result
