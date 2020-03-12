from django.shortcuts import render
from django import forms
import hello.habiterDB as db
import psycopg2
import requests
from requests.auth import HTTPBasicAuth
import logging
logger = logging.getLogger(__name__)

LEETCODE_LABELS = (
    ('Easy', 'Leetcode Easy Problem'),
    ('Medium', 'Leetcode Medium Problem'),
    ('Hard', 'Leetcode Hard Problem')
    )

class InputContentForm(forms.Form):
    link = forms.CharField()
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

def content(request):
    input_content_form = InputContentForm(request.POST)
    alert, error = None, None
    if input_content_form.is_valid():
        link = input_content_form.cleaned_data.get('link')
        label = input_content_form.cleaned_data.get('label')
        try:
            response =  db.add_community_content_item(
                    link,
                    label,
                    'Leetcode'
                    )
            alert = "Content uploaded succesfully, "+"|".join([link, label])
        except psycopg2.Error as e:
            # unique violation constraint
            # https://www.postgresql.org/docs/current/errcodes-appendix.html#ERRCODES-TABLE
            if e.pgcode == "23505": 
                error = "Oops.. You are trying to insert content that is already present!"
                error += "\n\n"+e.pgerror
            else:
                error = "Oops.. Looks like there is some problem in uploading your content:"
                error += "\n\n"+e.pgerror

    content = db.get_community_content("Leetcode")
    return render(request, "content.html", {
        'community_content': content,
        'input_content_form': input_content_form,
        'alert':alert,
        'error':error
        })

class TeamForm(forms.Form):
    team_name = forms.CharField()
    team_invite = forms.CharField()
    timezone = forms.CharField()

class LeetcodeTeamForm(TeamForm):
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

def compute_teams_capacity(teams, name='Total Capacity', timezone=None):
    """
    timezone=None for overall capacity
    timezone='pst' for timezone specific capacity


    given a set of teams compute how many people can hold 
    from this query 
    SELECT id, team_name, sent, claimed, link, label, timezone, session_time FROM teams

    returns
        'total_teams_len':len(teams),
        'open_teams_len':0,
        'open_capacity':0
    """
    MAX_CAPACITY = 3
    capacity_info = {
        'total_teams_len':len(teams),
        'open_teams_len':0,
        'open_capacity':0,
        'name':name
    }
    if timezone:
        capacity_info['total_teams_len'] = len([team for team in teams if team[6] == timezone])
    for team in teams:
        # team[4]: link
        if (team[4] != "https://habiter.app") and (not timezone or (timezone and team[6] == timezone)):
            # team[3] : claimed
            if int(team[3]) < MAX_CAPACITY:
                capacity_info['open_teams_len']+=1
                capacity_info['open_capacity']+=MAX_CAPACITY - int(team[3])

    # this  is to pass to progress bar
    capacity_info['open_teams_ratio'] = str(capacity_info['open_teams_len']/capacity_info['total_teams_len'] * 100)+"%"
    return capacity_info

def teams(request):
    alert, error =  None, None
    team_form = LeetcodeTeamForm(request.POST)
    if team_form.is_valid():
        team_invite = team_form.cleaned_data['team_invite']
        team_name = team_form.cleaned_data['team_name']
        timezone = team_form.cleaned_data['timezone']
        label = team_form.cleaned_data.get('label')
        response = add_community_team(
                "Leetcode",
                team_invite,
                team_name,
                timezone,
                label
                )
        alert = "Content added succesfully: "+" | ".join([team_name, team_invite, timezone, label])

    teams = db.get_community_teams("Leetcode")
    capacity = {
            'overall':compute_teams_capacity(teams),
            }
    for timezone in ['pst','est','gmt','ist','gmt+8']:
        capacity[timezone] = compute_teams_capacity(
                teams, 
                timezone=timezone,
                name=timezone+" capacity"
                )
    capacity['gmt8'] = capacity['gmt+8']

    print("capacity")
    print(capacity)
    return render(request, "teams.html", {
        'teams':teams,
        'capacity':capacity,
        'team_form':team_form,
        'alert':alert,
        'error':error
        })

def _get_amplitude_chart(chart_id):
    """
    Habiter DAU: yzev0y5
    """
    data = requests.get('https://amplitude.com/api/3/chart/'+chart_id+'/query', auth=HTTPBasicAuth("037a7d00104197145a748cc912540b81", "c3a810b9cc0f1f0bddec7a7ecb710884"))
    return data.json()

def amplitude__Habiter_DAU():
    """
    return list of timeseries
    return [ [(#, setId, value), .. ] .. ]
    """
    json_data = _get_amplitude_chart('yzev0y5')
    timeseries = json_data['data']['series']
    labels = json_data['data']['xValues']
    return timeseries, labels
    

def index(request):
    alert, error =  None, None
    teams = db.get_community_teams("Leetcode")
    capacity = {
            'overall':compute_teams_capacity(teams),
            }
    Habiter_DAU, xlabels = amplitude__Habiter_DAU()
    amplitude = {
            'DAU_screenshots': [*map(lambda x: x['value'], Habiter_DAU[0])],
            'DAU': [*map(lambda x: x['value'], Habiter_DAU[1])],
            'xlabels':xlabels,
    }
    logger.warning(amplitude)
    return render(request, "admin/index.html", {
        'amplitude':amplitude,
        'teams':teams,
        'capacity':capacity,
        'alert':alert,
        'error':error
        })

def users(request):
    alert, error = None, None
    users = db.get_community_users("Leetcode")
    return render(request, "users.html", {
        'users':users,
        'alert':alert,
        'error':error
        })

def landing(request):
    return render(request, "landing.html")



