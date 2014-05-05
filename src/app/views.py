#!/usr/bin/env python

from django.views.generic.list import ListView
from django.views.generic import TemplateView, DetailView
from django.http import Http404
from rest_framework import generics

import models
import serializers


class IndexView(TemplateView):
    template_name = 'index.tmpl.html'


class BatteryDetailView(DetailView):
    template_name = 'battery.tmpl.html'
    context_object_name = 'battery'

    def get_object(self, queryset=None):
        batteries = [s for s in models.PowerSource.get_all()
                     if s.is_battery and s.slug==self.kwargs.get('slug')]
        if not batteries: raise Http404
        return batteries.pop()


class PowerSourcePageView(ListView):
    template_name = 'batteries.tmpl.html'

    def get_queryset(self, *args, **kw):
        return [source for source in models.PowerSource.get_all() if source.is_battery]

    def get_context_data(self, **kwargs):
        context = super(PowerSourcePageView, self).get_context_data(**kwargs)
        context['battery_list'] = [s for s in models.PowerSource.get_all() if s.is_battery]
        return context


class AccessPointPageView(TemplateView):
    template_name = 'access_points.tmpl.html'


class AccessPointListView(generics.ListAPIView):
    serializer_class = serializers.AccessPointSerializer

    def get_queryset(self, *args, **kw):
        return models.AccessPoint.get_all()


class PowerSourceListView(generics.ListAPIView):
    serializer_class = serializers.PowerSourceSerializer

    def get_queryset(self, *args, **kw):
        return models.PowerSource.get_all()


class PowerSourceView(generics.RetrieveAPIView):
    serializer_class = serializers.PowerSourceSerializer

    def get_object(self, *args, **kw):
        source = models.PowerSource.get(id=self.kwargs.get('slug'))
        if source is None: raise Http404
        return source


class BatteryListView(PowerSourceListView):
    def get_queryset(self, *args, **kw):
        return [source for source in models.PowerSource.get_all() if source.is_battery]
