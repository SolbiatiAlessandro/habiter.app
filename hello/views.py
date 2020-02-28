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
        if not invite:
            logging.error("!!INVITE ARE FINISHED for timezone "+timezone+"!!")
            raise Exception
        (invite_id, team_invite_link, team_name) = invite
        data = {
            'invite_id': invite_id,
            'team_invite_link': team_invite_link,
            'team_name': team_name
        }
        return JsonResponse(data)
    except Exception as e:
        logging.error("!!ERROR in leetcode_match")
        logging.error(e)
        data = {
            'invite_id': -1,
            'team_invite_link': 'https://t.me/leetcode_feb_2019',
            'team_name': 'FEB 2020 TEAM'
        }
        return JsonResponse(data)

def leetcode_invite_sent_confirmation(request):
    """
    confirmed that invite was sent, we assume the user
    joined the event 

    request:{
    'invite_id':2
    }
    """
    invite_id = request.GET.get('invite_id', None)
    if not invite_id:
        logger.error("ERROR!!!!send confirmation is breaking because no invite_id provided")
        logger.error(request.GET)
    db__leetcode_invite_sent_confirmation(invite_id)
    return JsonResponse({'result':'SUCCESS'})



def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
