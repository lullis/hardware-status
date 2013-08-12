#!/usr/bin/env python

import json

from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView, ListView

import models


class IndexView(TemplateView):
    template_name = 'index.tmpl.html'


class BatteryListView(ListView):
    template_name = 'batteries.tmpl.html'
    model = models.Battery

    def dispatch(self, *args, **kw):
        models.Battery.get_all()
        return super(BatteryListView, self).dispatch(*args, **kw)


class BatteryView(DetailView):
    template_name = 'battery.tmpl.html'
    model = models.Battery


class AccessPointListView(TemplateView):
    template_name = 'access_points.tmpl.html'


def access_points(request):
    return HttpResponse(json.dumps([{
        'ssid': ap.ssid
        } for ap in models.AccessPoint.get_all()]))


def battery_data(request, slug):
    battery, created = models.Battery.objects.get_or_create(slug=slug)
    battery.sync()
    battery.make_reading()
    remaining_time = battery.remaining_time
    data = {
        'charge_pct': battery.percentage_charge,
        'status': battery.status,
        'criticality_message': battery.charge_criticality_message
        }
    
    if remaining_time:
        remaining_minutes = remaining_time/60
        remaining_hours = remaining_minutes/60
        
    data['remaining_time'] = remaining_time and {
        'hours': remaining_hours,
        'minutes': '%02d' % (remaining_minutes % 60)
        }
    return HttpResponse(json.dumps(data))
