from django.shortcuts import render
from django.http import HttpResponse
import logging

from .models import Greeting

# Create your views here.
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
            'pitch':"<h3>What's this?</h3><p>We are a <b>community of founders</b> that gets together online every Tuesday to build their product</p><h3>What do we do?</h3><p>We all start building at the <b>same hour</b>. Join the event and you will be <b>paired up</b> with another founder to keep accountable and chat with.</p>",
            'footer':""
            }
    return render(request, "invite.html", context)

def sus(request):
    context = {
            'eventID':"ck6fj3jp79wt50128vfoj8t3u",
            'inviterID':None,
            'pitch':"Join the SUS event on Habiter",
            'footer':""
            }
    return render(request, "invite.html", context)

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
