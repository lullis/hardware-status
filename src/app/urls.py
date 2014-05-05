#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static

import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^power$', views.PowerSourcePageView.as_view(), name='power'),
    url(r'^power/battery/(?P<slug>\w+)$', views.BatteryDetailView.as_view(), name='battery-detail'),
    url(r'^wlan$', views.AccessPointPageView.as_view(), name='access-points'),
    url(r'^api/', include('app.api'))
)

if settings.DEBUG:
   urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
