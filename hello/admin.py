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

NO_COMMUNITY = "(oops.. no community found)"
NO_EMAIL = "(oops.. no email found)"

HABITERBOT = 'habiterbot'

class InputContentForm(forms.Form):
    link = forms.CharField()
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

class EditBotForm(forms.Form):
    def __init__(self, *args, descriptions=None):
        super(EditBotForm, self).__init__(*args)
        self.fields['description'].choices = descriptions
    description = forms.ChoiceField()
    content = forms.CharField( widget=forms.Textarea )

def content(request):
    input_content_form = InputContentForm(request.POST)
    alert, error = None, None
    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"

    # Accountability Session Material
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

    teams = db.get_community_teams(community)
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
        'error':error,
        'community':community,
        'email':email
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
    capacity = {
            'overall':compute_teams_capacity(teams),
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
    return render(request, "admin/index.html", {
        'amplitude':amplitude,
        'teams':teams,
        'capacity':capacity,
        'community':community,
        'email':email,
        'alert':alert,
        'error':error
        })

def users(request):
    alert, error = None, None
    community = request.session.get('community', NO_COMMUNITY)
    email = request.session.get('email', NO_EMAIL)
    if community == NO_COMMUNITY or email == NO_EMAIL:
        error = "oops.. looks like we didn't find your community/email properly. If this is unexpected call +44779648936 to get it fixed ASAP"
    users = db.get_community_users(community)
    return render(request, "users.html", {
        'users':users,
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
