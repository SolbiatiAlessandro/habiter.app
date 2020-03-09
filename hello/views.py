from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import logging
logger = logging.getLogger(__name__)

from .models import Greeting

# Create your views here.
def about(request):
    return render(request, "about.html")

def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "index.html")

def invite(request):
    context = {
            'eventID':request.GET.get('eventID','no ID provided'),
            'inviterID':request.GET.get('inviterID','no ID provided'),
            'pitch':"Habiter: get stuff done by inviting your friend to join you remotely for accountability and a sense of community.",
            'footer':"",
            }
    return render(request, "invite.html", context)

def pioneer(request):
    context = {
            'eventID':"ck6fj3jp79wt50128vfoj8t3u",
            'inviterID':None,
            'pitch':"<h3>What's this?</h3><p>We are a <b>community of founders</b> that gets together online every Tuesday to build their product</p><h3>What do we do?</h3><p>We all start building at the <b>same hour</b>. Join the event and you will be <b>paired up</b> with another founder to keep accountable and chat with.h3> </p> Get the most out of it </h3><p>Start by sending a message describing your project and have your buddy explain it back to you.</p>",
            'footer':""
            }
    return render(request, "invite.html", context)

def sus(request):
    context = {
            'eventID':"ck6fj3jp79wt50128vfoj8t3u",
            'inviterID':None,
            'pitch':"<h3>What's this?</h3><p>We are a <b>community of founders</b> that gets together online every Tuesday to build their product</p><h3>What do we do?</h3><p>We all start building at the <b>same hour</b>. Join the event and you will be <b>paired up</b> with another founder to keep accountable and chat with.</p><h3> Get the most out of it </h3><p>Start by sending a message describing your project and have your buddy explain it back to you.</p>",
            'footer':""
            }
    return render(request, "invite.html", context)

def builders(request):
    return render(request, "builders.html")

from hello.matching import db__get_leaderboard
def leetcode(request):
    leaderboard = db__get_leaderboard()
    return render(request, "leetcode.html", {'leaderboard': leaderboard})

from django import forms
#DEPRECATED
class LeetcodeProblemsForm(forms.Form):
    link1 = forms.CharField()
    link2 = forms.CharField()

LEETCODE_LABELS = (
    ('Easy', 'Leetcode Easy Problem'),
    ('Medium', 'Leetcode Medium Problem'),
    ('Hard', 'Leetcode Hard Problem')
    )

class InputContentForm(forms.Form):
    link = forms.CharField()
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

class TeamForm(forms.Form):
    team_name = forms.CharField()
    team_invite = forms.CharField()
    timezone = forms.CharField()

class LeetcodeTeamForm(TeamForm):
    label = forms.ChoiceField(choices=LEETCODE_LABELS)

class EditBotForm(forms.Form):
    content_id = forms.CharField()
    new_content = forms.CharField()


from hello.habiterDB import get_community_content, add_community_content_item, get_community_teams_by_timezone, add_community_team, get_bot_content, edit_bot_content
def leetcode_admin(request):
    # TIME HEAVY QUERY
    teams = {
        'pst':get_community_teams_by_timezone("Leetcode", "pst"),
        'est':get_community_teams_by_timezone("Leetcode", "est"),
        'gmt':get_community_teams_by_timezone("Leetcode", "gmt"),
        'ist':get_community_teams_by_timezone("Leetcode", "ist"),
        'gmt8':get_community_teams_by_timezone("Leetcode", "gmt+8"),
    }
    #teams = {}
    alert = None

    input_content_form = InputContentForm(request.POST)
    if input_content_form.is_valid():
        link = input_content_form.cleaned_data.get('link')
        label = input_content_form.cleaned_data.get('label')
        response =  add_community_content_item(
                link,
                label,
                'Leetcode'
                )
        alert = "Content added succesfully: "+link+", "+label

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


    bot_form = EditBotForm(request.POST)
    if bot_form.is_valid():
        content_id  = bot_form.cleaned_data['content_id']
        new_content  = bot_form.cleaned_data['new_content']
        edit_bot_content(content_id, new_content)
        alert = "Content added succesfully: "+" | ".join([content_id, new_content])

    bot_content =  get_bot_content()

    return render(request, "admin.html", 
                {
                    'community_content':  get_community_content("Leetcode"),
                    'teams': teams,
                    'input_content_form': input_content_form,
                    'team_form': team_form,
                    'form_action': '/leetcode_admin',
                    'admin_title': "Leetcode",
                    'alert': alert,
                    'bot_content':bot_content,
                    'bot_form':bot_form
                }
            )


from hello.matching import get_community_team_invite, sent_invite
def leetcode_match(request):
    """
    matches a new team for leetcode

    request: 
    {
    'timezone':'pst'
    }
    """
    # THIS IS UGLY BUT NEED TO CATCH ALL EXCPETION, OTHERWISE WE LOSE USERS
    try:
        timezone = request.GET.get('timezone', None)
        invite = get_community_team_invite("Leetcode", timezone)
        (team_id, team_invite_link, team_name) = invite
        data = {
            'team_id': team_id,
            'team_invite_link': team_invite_link,
            'team_name': team_name
        }
        return JsonResponse(data)
    except Exception as e:
        logging.error("!!ERROR in leetcode_match")
        logging.error(e)
        data = {
            'team_id': -1,
            'team_invite_link': 'https://t.me/leetcode_feb_2019',
            'team_name': 'FEB 2020 TEAM'
        }
        return JsonResponse(data)

def leetcode_invite_sent_confirmation(request):
    """
    confirmed that invite was sent, we assume the user
    joined the event 

    request:{
    'team_id':2
    }
    """
    team_id = request.GET.get('team_id', None)
    if not team_id:
        logger.error("ERROR!!!!send confirmation is breaking because no team_id provided")
        logger.error(request.GET)
        return JsonResponse({'result':'ERROR: no team_id provided'})

    sent_invite(team_id)
    return JsonResponse({'result':'SUCCESS'})

def founders(request):
    return render(request, "founders.html")

from hello.matching import db__get_next_founders_team_invite, db__founders_invite_sent_confirmation

def founders_match(request):
    logger.warning("founders_match")
    # THIS IS UGLY BUT NEED TO CATCH ALL EXCPETION, OTHERWISE WE LOSE USERS
    try:
        timezone = request.GET.get('timezone', None)
        invite = db__get_next_founders_team_invite(timezone)
        (team_id, team_invite_link, team_name) = invite
        data = {
            'team_id': team_id,
            'team_invite_link': team_invite_link,
            'team_name': team_name
        }
        return JsonResponse(data)
    except Exception as e:
        logging.error("!!ERROR in leetcode_match")
        logging.error(e)
        data = {
            'team_id': -1,
            'team_invite_link': 'https://t.me/leetcode_feb_2019',
            'team_name': 'FEB 2020 TEAM'
        }
        return JsonResponse(data)

def founders_invite_sent_confirmation(request):
    logger.warning("founders_invite_sent_confirmation")
    team_id = request.GET.get('team_id', None)

    db__founders_invite_sent_confirmation(team_id)
    return JsonResponse({'result':'SUCCESS'})

from hello.matching import db__get_all_founders_clubs, db__add_founders_club
def founders_admin(request):
    # TIME HEAVY QUERY
    teams = {
        'pst':db__get_all_founders_clubs("pst"),
        'est':db__get_all_founders_clubs("est"),
        'gmt':db__get_all_founders_clubs("gmt"),
        'ist':db__get_all_founders_clubs("ist"),
        'gmt8':db__get_all_founders_clubs("gmt+8"),
    }
    team_form = TeamForm(request.POST)
    if team_form.is_valid():
        response = db__add_founders_club(
                team_form.cleaned_data['team_invite'],
                team_form.cleaned_data['team_name'],
                team_form.cleaned_data['timezone'],
                )

    return render(request, "admin.html", 
                {
                    'problems':  (('',''),('','')),
                    'teams': teams,
                    'problems_form': {""},
                    'team_form': team_form,
                    'form_action': '/founders_admin',
                    'admin_title': "Founders"
                }
            )

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
