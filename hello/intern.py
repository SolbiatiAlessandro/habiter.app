"""
Internal tools for Habiter dev
"""
from django.shortcuts import redirect

def docs(request):
    return redirect("http://habiter-docs.herokuapp.com/")

def cicd(request):
    return redirect("https://travis-ci.com/github/SolbiatiAlessandro/HabiterBot")

def codecoverage(request):
    return redirect("https://codecov.io/gh/SolbiatiAlessandro/HabiterBot")

def github_HabiterBot(request):
    return redirect("https://github.com/SolbiatiAlessandro/HabiterBot")
