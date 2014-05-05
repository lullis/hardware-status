#!/usr/bin/env python

from rest_framework import serializers

class AccessPointSerializer(serializers.Serializer):
    SSID = serializers.CharField(source='ssid', read_only=True)
    signal_strength = serializers.IntegerField(read_only=True)


class PowerSourceSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    capacity = serializers.FloatField(read_only=True, source='Capacity')
    time_to_empty = serializers.IntegerField(read_only=True, source='TimeToEmpty')
    time_to_full = serializers.IntegerField(read_only=True, source='TimeToFull')
    percentage = serializers.FloatField(read_only=True, source='Percentage')
    id = serializers.CharField(read_only=True)
