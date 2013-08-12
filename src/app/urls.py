#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, url
from django.conf.urls.static import static

import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^batteries$', views.BatteryListView.as_view(), name='battery_list'),
    url(r'^battery/(?P<slug>\w+)$', views.BatteryView.as_view(), name='battery_detail'),
    url(r'^battery/(?P<slug>\w+)\.js$', views.battery_data, name='battery_data'),
    url(r'^access-points$', views.AccessPointListView.as_view(), name='access_point_list'),
    url(r'^access-points.js$', views.access_points, name='access_point_data')
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
        )
