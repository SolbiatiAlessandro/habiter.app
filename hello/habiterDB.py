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

def get_community_content(community):
    """
    like _get_community_content
    but augment with content index information
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, link, label FROM content WHERE community = %s ORDER BY id;", (community,))
    content = cur.fetchall()
    #cur.execute("SELECT id, team_name, content_index FROM teams WHERE community = %s;", (community,))
    cur.execute("SELECT id, team_name, content_index FROM leetcode_teams;")
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
    
