from django.shortcuts import render
from django.http import HttpResponse
import logging

from .models import Greeting

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "index.html")

def invite(request):
    logging.warning("DJANGO: invite")
    logging.warning(request)
    logging.warning(request.GET.get('inviteID', ''))
    context = {'inviteID':request.GET.get('inviteID','no ID provided')}
    return render(request, "invite.html", context)


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
