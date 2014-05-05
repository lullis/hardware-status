#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^power/sources$', views.PowerSourceListView.as_view()),
    url(r'^power/source/(?P<slug>\w+)$', views.PowerSourceView.as_view(), name='api-power-source'),
    url(r'^power/batteries$', views.BatteryListView.as_view()),
    url(r'^network/access-points$', views.AccessPointListView.as_view(), name='api-access-points')
)
