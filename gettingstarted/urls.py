from django.urls import path, include
from django.conf.urls import url

from django.contrib import admin

admin.autodiscover()

import hello.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("leetcode", hello.views.leetcode),
    path("leetcode_admin", hello.views.leetcode_admin),
    path("SUS", hello.views.sus),
    path("pioneer", hello.views.pioneer),
    path("invite", hello.views.invite),
    path("about", hello.views.about),
    path("builders", hello.views.builders),
    path("", hello.views.index, name="index"),
    path("db/", hello.views.db, name="db"),
    path("admin/", admin.site.urls),
    url(r'^ajax/leetcode_match/$', hello.views.leetcode_match, name='leetcode_match'),
    url(r'^ajax/leetcode_invite_sent_confirmation/$', hello.views.leetcode_invite_sent_confirmation, name='leetcode_invite_sent_confirmation'),
]
