from django.shortcuts import render
from django import forms
import psycopg2
import requests
from time import time
from requests.auth import HTTPBasicAuth
import logging
import traceback
logger = logging.getLogger(__name__)

import hello.habiterDB as db
import  hello.matching as matching

LEETCODE_LABELS = (
    ('Easy', 'Leetcode Easy Problem'),
    ('Medium', 'Leetcode Medium Problem'),
    ('Hard', 'Leetcode Hard Problem')
    )

NO_COMMUNITY = "(oops.. no community found)"
NO_EMAIL = "(oops.. no email found)"

HABITERBOT = 'habiterbot'


class InputContentForm(forms.Form):
    def __init__(self, *args, labels=None):
        super(InputContentForm, self).__init__(*args)
        if not labels:
            self.fields['label'].choices = [['No Label', 'No Label']]
        else:
            self.fields['label'].choices = labels
    link = forms.CharField()
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

class EditBotForm(forms.Form):
    def __init__(self, *args, descriptions=None):
        super(EditBotForm, self).__init__(*args)
        self.fields['description'].choices = descriptions
    description = forms.ChoiceField()
    content = forms.CharField( widget=forms.Textarea )

def content(request):
    alert, error = None, None
    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"

    # Accountability Session Material
    _content_labels = db.get_community_content_labels(community)
    content_labels = [(label[0], label[0]) for label in _content_labels]
    # content_labels might be None, in case put No Label
    input_content_form = InputContentForm(request.POST, labels=content_labels)

    if input_content_form.is_valid():
        link = input_content_form.cleaned_data.get('link')
        label = input_content_form.cleaned_data.get('label')
        try:
            response =  db.add_community_content_item(
                    link,
                    label,
                    community
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
    content = db.get_community_content(community)

    # Bots Content
    bot_content = db.get_bot_content_by_community(community) 
    # id, description, content
    descriptions = [(content[1], content[1]) for content in bot_content]
    edit_bot_form = EditBotForm(request.POST, descriptions=descriptions)

    # Accountability Session Material
    if edit_bot_form.is_valid():
        description = edit_bot_form.cleaned_data.get('description')
        content = edit_bot_form.cleaned_data.get('content')
        try:
            response =  db.edit_bot_content_from_description(
                    description,
                    community,
                    content
                )
            if response == 1:
                alert = "Bot edit successful, "+"|".join([description, content])
            else:
                error = "ehmm.. maybe the edit didn't work since we just updated {} rows".format(response) 
        except psycopg2.Error as e:
            error = "Oops.. Looks like there is some problem in uploading your content:"
            error += "\n\n"+e.pgerror


    return render(request, "content.html", {
        'community_content': content,
        'input_content_form': input_content_form,
        'edit_bot_form': edit_bot_form,
        'alert':alert,
        'error':error,
        'community':community,
        'email':email,
        'bot_content':bot_content
        })

class TeamForm(forms.Form):
    team_name = forms.CharField()
    team_invite = forms.CharField()
    timezone = forms.CharField()

class LeetcodeTeamForm(TeamForm):
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

def compute_teams_capacity(teams, name='Total Capacity', timezone=None, MAX_CAPACITY=3):
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
    capacity_info['open_teams_ratio'] = str(capacity_info['open_teams_len']/capacity_info['total_teams_len'] * 100)+"%"  if capacity_info['total_teams_len'] > 0 else 0
    return capacity_info

def teams(request):
    alert, error =  None, None
    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"
    team_form = LeetcodeTeamForm(request.POST)
    if team_form.is_valid():
        team_invite = team_form.cleaned_data['team_invite']
        team_name = team_form.cleaned_data['team_name']
        timezone = team_form.cleaned_data['timezone']
        label = team_form.cleaned_data.get('label')
        response = add_community_team(
                community,
                team_invite,
                team_name,
                timezone,
                label
                )
        alert = "Content added succesfully: "+" | ".join([team_name, team_invite, timezone, label])

    _teams = db.get_community_teams(community)
    try:
        teams = db.get_community_teams_with_activity_data(community)
    except Exception as e:
        logging.error("ERROR: db.get_community_teams_with_activity_data")
        traceback.print_exc()
        error = e
        teams = _teams
    logger.warning("get_community_teams: "+str(len(teams)))
    team_size = db.get_community_team_size(community)
    logger.warning("get_community_team_size: "+str(team_size))

    capacity = {
            'overall':compute_teams_capacity(_teams, MAX_CAPACITY=team_size),
            }
    for timezone in ['pst','est','gmt','ist','gmt+8']:
        timezone_teams = matching._select_new_teams(community, timezone)
        capacity[timezone] = compute_teams_capacity(
                timezone_teams, 
                timezone=timezone,
                name=timezone+" capacity",
                MAX_CAPACITY=team_size
                )
    capacity['gmt8'] = capacity['gmt+8']

    print("capacity")
    print(capacity)
    return render(request, "teams.html", {
        'teams':teams,
        'capacity':capacity,
        'team_form':team_form,
        'alert':alert,
        'error':error,
        'community':community,
        'email':email,
        'team_size':team_size
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
    loginForm = LoginForm(request.POST)
    if loginForm.is_valid():
        community = loginForm.cleaned_data.get('community')
        email = loginForm.cleaned_data.get('email')

        admin = db.get_community_admin(community)
        if not admin or admin[0][0] != email:
            logger.warning("Warning! Login with wrong credentials")
            logger.warning(email, community)
            return render(request, "login.html", {
                'login_form':loginForm,
                'alert':alert,
                'error':"Sorry, looks like that {} is not an admin for {}".format(email, community)
                })

        request.session['community'] = community 
        request.session['email'] = email

    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"

    teams = db.get_community_teams(community)
    logger.warning("get_community_teams: "+str(len(teams)))
    team_size = db.get_community_team_size(community)
    logger.warning("get_community_team_size: "+str(team_size))
    capacity = {
            'overall': compute_teams_capacity(teams,MAX_CAPACITY=team_size),
            }

    if community == "Leetcode":
        Habiter_DAU, xlabels = amplitude__Habiter_DAU()
        amplitude = {
                'DAU_screenshots': [*map(lambda x: x['value'], Habiter_DAU[0])],
                'DAU': [*map(lambda x: x['value'], Habiter_DAU[1])],
                'xlabels':xlabels,
        }
    else:
        # TODO: we need to put activity graph cross-community
        amplitude = {
            'DAU_screenshots': [],
            'DAU': [],
            'xlabels': [],
        }
    logger.warning(amplitude)
    # getting master group link for promotion
    master_team_info = db.get_community_master_team(community)
    community_master_group_link = master_team_info[4] if master_team_info else '(no master team)'
    return render(request, "admin/index.html", {
        'amplitude':amplitude,
        'teams':teams,
        'capacity':capacity,
        'community':community,
        'community_master_group_link':community_master_group_link,
        'email':email,
        'alert':alert,
        'error':error
        })

def users_backfill(request):
    alert, error = None, None
    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"
    try:
        start = time()
        db.user_action_backfill(community)
        end = time()
        alert= "Data Refreshed Successfully! (backfill took {} seconds)".format(str(end - start))
    except Exception as e:
        logging.error("ERROR: user_action_backfill broke")
        traceback.print_exc()
        error = e
    return users(request, alert=alert, error=error)

def users(request, alert=None, error=None):
    #alert, error = None, None
    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"
    users = db.get_community_users_additional_columns(community)

    logger.warning('computing users_timeserie')
    # this is to measure user growth over time
    users_timeserie = {'labels':[],'values':[]}
    # #	Username	session_active_total	session_skip_total	session_skip_streak	days_active_total	days_since_join
    days_since_join_col = 6
    # unknown starting date is put at the start of the labels
    max_day = max(user[days_since_join_col] for user in users if user[days_since_join_col] is not None )
    days_since_join = [user[days_since_join_col] if user[days_since_join_col] else max_day+1 for user in users]
    users_timeserie['labels'] = [*range(-1, max_day + 1)]
    users_timeserie['values'] = [days_since_join.count(max_day - day) for day in users_timeserie['labels']]
    #we want the cum sum of users
    cumsum = 0
    for i, val in enumerate(users_timeserie['values']):
        cumsum += users_timeserie['values'][i]
        users_timeserie['values'][i] = cumsum
    logger.warning(users_timeserie)

    # clean users
    for i, row in enumerate(users):
        for j, col in enumerate(row):
            if col == 'None' or not col:
                col = -1
            if j != 1 and j != 9 and j != 8: # username , timezone, label
                users[i][j] = int(col)
        
    return render(request, "users.html", {
        'users':users,
        'users_timeserie': users_timeserie,
        'alert':alert,
        'error':error,
        'community':community,
        'email':email
        })

def landing(request):
    return render(request, "landing.html")

class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['community'].choices = db.get_communities()
    email = forms.EmailField()
    community = forms.ChoiceField()

def login(request):
    alert, error = None, None
    loginForm = LoginForm(request.POST)
    return render(request, "login.html", {
        'login_form':loginForm, 
        'alert':alert,
        'error':error
        }
    )
