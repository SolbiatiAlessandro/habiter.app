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

def leetcode(request):
    return render(request, "leetcode.html")

from django import forms
class LeetcodeProblemsForm(forms.Form):
    link1 = forms.CharField()
    link2 = forms.CharField()

class TeamForm(forms.Form):
    team_name = forms.CharField()
    team_invite = forms.CharField()
    timezone = forms.CharField()

from hello.matching import db__get_all_leetcode_teams, db__get_active_leetcode_problems
from hello.matching import db__set_active_leetcode_problems, db__add_leetcode_team
def leetcode_admin(request):
    # TIME HEAVY QUERY
    teams = {
        'pst':db__get_all_leetcode_teams("pst"),
        'est':db__get_all_leetcode_teams("est"),
        'gmt':db__get_all_leetcode_teams("gmt"),
        'ist':db__get_all_leetcode_teams("ist"),
        'gmt8':db__get_all_leetcode_teams("gmt+8"),
    }
    problems_form = LeetcodeProblemsForm(request.POST)
    if problems_form.is_valid():
        response = db__set_active_leetcode_problems(problems_form.cleaned_data['link1'],problems_form.cleaned_data['link2'])

    team_form = TeamForm(request.POST)
    if team_form.is_valid():
        response = db__add_leetcode_team(
                team_form.cleaned_data['team_invite'],
                team_form.cleaned_data['team_name'],
                team_form.cleaned_data['timezone'],
                )

    return render(request, "admin.html", 
                {
                    'problems':  db__get_active_leetcode_problems(),
                    'teams': teams,
                    'problems_form': problems_form,
                    'team_form': team_form,
                    'form_action': '/leetcode_admin',
                    'admin_title': "Leetcode"
                }
            )


from hello.matching import db__get_next_leetcode_team_invite, db__leetcode_invite_sent_confirmation
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
        invite = db__get_next_leetcode_team_invite(timezone)
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

    db__leetcode_invite_sent_confirmation(team_id)
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
