from django.urls import path, include
from django.conf.urls import url

from django.contrib import admin

admin.autodiscover()

import hello.views, hello.admin, hello.external_apis.mail_chimp, hello.intern

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    # CUSTOMER FACING
    path("founders", hello.views.founders),
    path("leetcode", hello.views.leetcode),
    path("leetcode", hello.views.codeforces),
    path("leetcode_admin", hello.views.leetcode_admin),
    path("_leetcode_admin", hello.views._leetcode_admin),
    path("SUS", hello.views.sus),
    path("pioneer", hello.views.pioneer),
    path("invite", hello.views.invite),
    path("about", hello.views.about),
    path("builders", hello.views.builders),
    path("founders", hello.views.founders),
    path("founders_admin", hello.views.founders_admin),
    #path("", hello.views.index, name="index"),
    path("", hello.admin.landing, name="index"),
    path("db/", hello.views.db, name="db"),
    path("admin/", admin.site.urls),
    path("join/<str:community>", hello.views.join),

    # ADMIN
    url("community/login", hello.admin.login, name="community_login"),
    url("community/landing", hello.admin.landing, name="community_landing"),
    url("community/home", hello.admin.index, name="community_home"),
    url("community/users", hello.admin.users, name="community_users"),
    url("backfill/users", hello.admin.users_backfill, name="backfill_users"),
    url("community/teams", hello.admin.teams, name="community_teams"),
    url("community/content", hello.admin.content, name="community_content"),

    # AJAX
    url(r'^ajax/mailchimp_subscribe/$', hello.external_apis.mail_chimp.mailchimp_subscribe, name='mailchimp_subscribe'),
    url(r'^ajax/leetcode_match/$', hello.views.leetcode_match, name='leetcode_match'),
    url(r'^ajax/match/$', hello.views.match, name='match'),
    url(r'^ajax/leetcode_invite_sent_confirmation/$', hello.views.leetcode_invite_sent_confirmation, name='leetcode_invite_sent_confirmation'),
    url(r'^ajax/invite_sent_confirmation/$', hello.views.invite_sent_confirmation, name='invite_sent_confirmation'),
    url(r'^ajax/founders_match/$', hello.views.founders_match, name='founders_match'),
    url(r'^ajax/founders_invite_sent_confirmation/$', hello.views.founders_invite_sent_confirmation, name='founders_invite_sent_confirmation'),

    # INTERNAL TOOLS
    path("docs", hello.intern.docs),
    path("ci", hello.intern.cicd),
    path("cc", hello.intern.codecoverage),
    path("codecoverage", hello.intern.codecoverage),
    path("git", hello.intern.github_HabiterBot),
    path("github", hello.intern.github_HabiterBot),
]
