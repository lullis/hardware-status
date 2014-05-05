#!/usr/bin/env python
import os
import datetime

import dbusx

POWER_SOURCES = [
    'Unknown',
    'Line Power',
    'Battery',
    'Ups',
    'Monitor',
    'Mouse',
    'Keyboard',
    'Pda',
    'Phone'
]

POWER_SOURCE_STATE = [
    'Unknown',
    'Charging',
    'Discharging',
    'Empty',
    'Fully charged',
    'Pending charge',
    'Pending discharge'
    ]

POWER_SOURCE_TECHNOLOGY = [
    'Unknown',
    'Lithium ion',
    'Lithium polymer',
    'Lithium iron phosphate',
    'Lead acid',
    'Nickel cadmium',
    'Nickel metal hydride'
    ]

NETWORK_DEVICE_STATES = [
    'Unknown',
    'Unmanaged',
    'Unavailable',
    'Disconnected',
    'Prepare',
    'Config',
    'Need Auth',
    'IP Config',
    'IP Check',
    'Secondaries',
    'Activated',
    'Deactivating',
    'Failed'
    ]

# [u'Capacity', u'PowerSupply', u'IsRechargeable', u'State', u'Online', u'Percentage', u'Type', u'UpdateTime', u'Vendor', u'TimeToFull', u'IsPresent', u'HasHistory', u'RecallUrl', u'EnergyRate', u'EnergyEmpty', u'Voltage', u'TimeToEmpty', u'Model', u'EnergyFullDesign', u'Energy', u'HasStatistics', u'NativePath', u'RecallVendor', u'EnergyFull', u'Serial', u'Technology', u'RecallNotice']


class PowerManager(object):
    NAMESPACE = 'org.freedesktop.UPower'

    def __init__(self):
        self.bus = dbusx.Connection(dbusx.BUS_SYSTEM)
        self.proxy = self.bus.proxy(self.NAMESPACE, '/org/freedesktop/UPower')

    @property
    def sources(self):
        return [PowerSource(self, device_path) for device_path in self.proxy.EnumerateDevices()]


class PowerSource(object):
    NAMESPACE = 'org.freedesktop.UPower.Device'

    def __init__(self, power_manager, device_path):
        self._manager = power_manager
        self.proxy = power_manager.bus.proxy(power_manager.NAMESPACE, device_path)

    @property
    def properties(self):
        self.proxy.Refresh()
        return {k: v[1] for (k, v) in self.proxy.GetAll(self.NAMESPACE).items()}

    @property
    def is_battery(self):
        return self.Type == POWER_SOURCES.index('Battery')

    @property
    def id(self):
        return os.path.basename(self.NativePath)

    @property
    def slug(self):
        return self.id

    @property
    def name(self):
        return '%s %s (%s)' % (self.Vendor, self.Model, self.Serial)

    @property
    def remaining_time(self):
        if self.status not in ['Charging', 'Discharging']: return None
        time = self.TimeToFull if self.State == 'Charging' else self.TimeToEmpty
        delta = datetime.timedelta(seconds=time)

        return {
            'seconds': delta.seconds % 60,
            'minutes': (delta.seconds / 60) % 60,
            'hours': (delta.seconds / (60 * 60)) % 24,
            'days': delta.days
            }

    @property
    def percentage_charge(self):
        return self.Percentage

    @property
    def technology(self):
        return POWER_SOURCE_TECHNOLOGY[self.Technology]

    @property
    def status(self):
        return POWER_SOURCE_STATE[self.State]

    def __getattr__(self, attribute):
        return self.properties.get(attribute)

    @staticmethod
    def get_all():
        return PowerManager().sources

    @staticmethod
    def get(**kw):
        sources = [source for source in PowerSource.get_all() if all([
            getattr(source, attr, None) == value for (attr, value) in kw.items()
            ])]
        return (sources and sources.pop()) or None


class NetworkDeviceManager(object):
    NAMESPACE = 'org.freedesktop.NetworkManager'

    def __init__(self):
        self.bus = dbusx.Connection(dbusx.BUS_SYSTEM)
        self.proxy = self.bus.proxy(self.NAMESPACE, '/org/freedesktop/NetworkManager')

    @property
    def devices(self):
        return [Device(self, device_path) for device_path in self.proxy.GetDevices()]


class Device(object):
    NAMESPACE = 'org.freedesktop.NetworkManager.Device.Wireless'

    def __init__(self, network_manager, device_path):
        self._manager = network_manager
        self._path = device_path
        self.proxy = network_manager.bus.proxy(network_manager.NAMESPACE, device_path)
        self.properties = self.get_properties()
        self.name = self.properties.get('Interface')

    def get_access_point_paths(self):
        if not self.is_wireless: return []
        return self.proxy.GetAccessPoints()

    def get_properties(self):
        namespace = 'org.freedesktop.NetworkManager.Device'
        return {k: v[1] for k, v in self.proxy.GetAll(namespace).items()}

    @property
    def is_wireless(self):
        return (self.properties.get('DeviceType') == 2)

    def state(self):
        # Network device state enum mapping is 0 indexed, but multiplied by 10 (0, 10, 20...)
        return NETWORK_DEVICE_STATES.index(self.properties.get('State')/10)


class AccessPoint(object):
    NAMESPACE = 'org.freedesktop.NetworkManager.AccessPoint'

    def __init__(self, network_manager, access_point_path):
        self.proxy = network_manager.bus.proxy(network_manager.NAMESPACE, access_point_path)
        self.properties = self.get_properties()

    def get_properties(self):
        return {k: v[1] for k, v in self.proxy.GetAll(self.NAMESPACE).items()}

    @property
    def ssid(self):
        return ''.join([str(byte) for byte in self.properties.get('Ssid')])

    @property
    def signal_strength(self):
        return int(self.properties.get('Strength'))

    @staticmethod
    def get_all():
        manager = NetworkDeviceManager()
        wireless_devices = [device for device in manager.devices if device.is_wireless]
        access_points = []

        for device in wireless_devices:
            for ap in device.get_access_point_paths():
                access_points.append(AccessPoint(manager, ap))

        return sorted(access_points, key=lambda it: it.signal_strength, reverse=True)
