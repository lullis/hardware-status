#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import url, patterns, include
from django.conf.urls.static import static



urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^about/', include('django.contrib.flatpages.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^author', include('authoring.urls')),
    url(r'^reporting/', include('reporting.urls')),
    url(r'^shop', include('shop.urls')),
    url(r'^study/', include('learning.urls')),
    url(r'^surveys/', include('survey.urls')),
    url(r'^urls.js$', full_urls, name='app-url-patterns'),
    url(r'^upload/?$', upload_file, name='app-file-upload'),
    url(r'^upload/progress$', uwsgi_upload_progress, name='app-file-upload-progress'),
    url(r'^upload/progress/(?P<progress_id>\w+).js$', uwsgi_upload_progress, name='app-file-upload-stats')
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.ASSETS_URL, document_root=settings.ASSETS_ROOT)
