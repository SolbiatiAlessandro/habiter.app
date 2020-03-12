from django.shortcuts import render
from django import forms
import hello.habiterDB as db
import psycopg2

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
    return render(request, "teams.html", {
        'teams':teams,
        'team_form':team_form,
        'alert':alert,
        'error':error
        })

def users(request):
    users = db.get_community_users("Leetcode")
    return render(request, "users.html", {
        'users':users
        })
