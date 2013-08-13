#!/usr/bin/env python
import os
import datetime

import dbus
from django.db import models
from django.template.defaultfilters import slugify

NETWORK_DEVICES = {
    1: 'Ethernet',
    2: 'Wi-Fi',
    5: 'Bluetooth',
    6: 'OLPC',
    7: 'WiMAX',
    8: 'Modem',
    9: 'InfiniBand',
    10: 'Bond',
    11: 'VLAN',
    12: 'ADSL'
    }

DEVICE_STATES = {
    0: 'Unknown',
    10: 'Unmanaged',
    20: 'Unavailable',
    30: 'Disconnected',
    40: 'Prepare',
    50: 'Config',
    60: 'Need Auth',
    70: 'IP Config',
    80: 'IP Check',
    90: 'Secondaries',
    100: 'Activated',
    110: 'Deactivating',
    120: 'Failed'
    }


class Battery(models.Model):
    name = models.CharField(max_length=200, default='Unknown')
    slug = models.SlugField()
    technology = models.CharField(max_length=200, default='Unknown')
    design_capacity = models.PositiveIntegerField(default=1)
    max_capacity = models.PositiveIntegerField(default=1)
    current_capacity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, default='Unknown')

    @property
    def design_capacity_mah(self):
        return '%d mAh' % (self.design_capacity / 1000)

    @property
    def max_capacity_mah(self):
        return '%d mAh' % (self.max_capacity / 1000)

    @property
    def current_capacity_mah(self):
        return '%d mAh' % (self.current_capacity / 1000)

    @property
    def percentage_charge(self):
        return int(100 * self.current_capacity / float(self.max_capacity))

    @property
    def charge_criticality_message(self):
        # This is a silly method. It's here just to make it easier for
        # the template to know which css class to add.

        pct = self.percentage_charge
        if 0 <= pct <= 25: return 'danger'
        elif 25 < pct <= 50: return 'warning'
        elif 50 < pct < 75: return 'success'
        else: return 'info'

    @property
    def remaining_time(self):
        rate = self._get_acpi_reported_rate() or self._get_sysfs_reported_rate()
        if not rate: return None

        return (self.current_capacity) / rate

    def _get_sysfs_reported_rate(self):
        # Only calculate time when it's discharging. Charging or full returns None
        readings = self.batteryreading_set.all()
        try:
            last_status_change = readings.exclude(status=self.status).latest().timestamp
        except Exception:
            last_status_change = datetime.datetime(1970, 1, 1) # Epoch

        readings = readings.filter(timestamp__gte=last_status_change, status=self.status)
        if not readings.count() >= 2: return None

        if self.status != 'discharging': return None

        latest = readings.latest()
        earliest = readings.order_by('timestamp')[0]

        delta_charge = latest.capacity - earliest.capacity
        if delta_charge == 0: return None

        delta_time = (latest.timestamp - earliest.timestamp).seconds
        return abs(int(delta_charge / delta_time))

    def _get_acpi_reported_rate(self):
        filename = '/proc/acpi/battery/%s/state' % self.slug
        with open(filename) as f:
            state = f.read()
            rate_line = [line for line in state.split('\n') if line.startswith('present rate:')]
            # there is a line in the format 'present rate: \d mW' Let's get the power.
            if rate_line:
                return int(int(rate_line[0].rstrip(' mW').split()[-1]) / 3.6)

        return None

    def _get_current_capacity(self):
        capacity = self.read_attribute('charge_now') or self.read_attribute('energy_now')
        return capacity and int(capacity) or None

    def read_attribute(self, attr):
        filename = '/sys/class/power_supply/%s/%s' % (self.slug, attr)
        if not os.path.exists(filename): return None

        with open(filename) as f:
            return f.read().strip()

    def sync(self):
        manufacturer = self.read_attribute('manufacturer').strip()
        model_name = self.read_attribute('model_name').strip()
        design_capacity = self.read_attribute('charge_full_design') or self.read_attribute('energy_full_design')
        max_capacity = self.read_attribute('charge_full') or self.read_attribute('energy_full')
        current_capacity = self._get_current_capacity()

        self.name = ' - '.join([manufacturer, model_name])
        self.technology = self.read_attribute('technology')
        if design_capacity: self.design_capacity = int(design_capacity)
        if max_capacity: self.max_capacity = int(max_capacity)
        if current_capacity: self.current_capacity = current_capacity
        self.status = slugify(self.read_attribute('status'))
        self.save()

    def make_reading(self):
        capacity = self._get_current_capacity()
        if capacity:
            return BatteryReading.objects.create(
                battery=self,
                capacity=capacity,
                status=slugify(self.read_attribute('status'))
            )
        return None

    @staticmethod
    def get_all():
        Battery.objects.all().delete()
        batteries = []
        power_supply_dir = '/sys/class/power_supply/'
        power_supplies = [
            ps for ps in os.listdir(power_supply_dir)
            if os.path.isdir(os.path.join(power_supply_dir, ps))
            ]

        for ps in power_supplies:
            battery = Battery()
            battery.slug = ps
            if battery.read_attribute('type') != 'Battery':
                continue
            battery.sync()
            batteries.append(battery)

        return batteries


class BatteryReading(models.Model):
    battery = models.ForeignKey(Battery)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Unknown')
    capacity = models.PositiveIntegerField()

    def __unicode__(self):
        return 'Battery %s reading at %s: %d (%s)' % (
            self.battery.slug, self.timestamp, self.capacity, self.status
            )

    class Meta:
        get_latest_by = 'timestamp'


class NetworkManager(object):
    NAMESPACE = 'org.freedesktop.NetworkManager'

    def __init__(self):
        self.bus = dbus.SystemBus()
        namespace = self.__class__.NAMESPACE
        proxy = self.bus.get_object(namespace, '/org/freedesktop/NetworkManager')
        self.manager = dbus.Interface(proxy, namespace)

    def get_devices(self):
        return [self.make_device(d) for d in self.manager.GetDevices()]

    def make_device(self, device_data):
        proxy = self.bus.get_object(self.__class__.NAMESPACE, device_data)
        return Device(proxy)

    def make_access_point(self, access_object_path):
        proxy = self.bus.get_object(self.__class__.NAMESPACE, access_object_path)
        return AccessPoint(proxy)


class Device(object):
    NAMESPACE = 'org.freedesktop.NetworkManager.Device.Wireless'

    def __init__(self, proxy):
        self.proxy = proxy
        self.properties = self.get_properties()
        self.name = self.properties.get('Interface')

    def get_access_point_paths(self):
        interface = dbus.Interface(self.proxy, self.__class__.NAMESPACE)
        if not self.is_wireless(): return []
        return interface.GetAccessPoints()

    def get_properties(self):
        iface = dbus.Interface(self.proxy, 'org.freedesktop.DBus.Properties')
        return iface.GetAll('org.freedesktop.NetworkManager.Device')

    def is_wireless(self):
        return (self.properties.get('DeviceType') == 2)

    def state(self):
        return DEVICE_STATES[self.properties.get('State')]


class AccessPoint(object):
    NAMESPACE = 'org.freedesktop.NetworkManager.AccessPoint'

    def __init__(self, proxy):
        self.proxy = proxy
        self.properties = self.get_properties()

    def get_properties(self):
        interface = dbus.Interface(self.proxy, 'org.freedesktop.DBus.Properties')
        return interface.GetAll(self.__class__.NAMESPACE)

    @property
    def ssid(self):
        return ''.join([str(byte) for byte in self.properties.get('Ssid')])

    @staticmethod
    def get_all():
        manager = NetworkManager()
        wireless_devices = [d for d in manager.get_devices() if d.is_wireless()]
        access_points = []

        for device in wireless_devices:
            for ap in device.get_access_point_paths():
                access_points.append(manager.make_access_point(ap))

        return access_points
