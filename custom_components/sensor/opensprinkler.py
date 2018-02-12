"""
 OpenSprinkler custom component for Home Assistant

 Author: Phil Mottin
 Version: 1.0
 Description: This is a work in progress.
              The component will fetch OpenSprinkler API and build a python dictionary into "<obj>.data['data']" attribute of OpenSprinklerData class"
              stations = <obj>.data['data']['stations']
              schedules = <obj>.data['data']['programs']
              settings = <obj>.data['data']['settings']
              options = <obj><obj>.data['data']['options']
              pump1 = <obj>.data['data']['pump1_index']
              pump2 = <obj>.data['data']['pump2_index']
              lastrun = <obj>.data['data']['lastrun']
              rain_delay_time = <obj>.data['data']['rain_delay_time']
              rain_delay = <obj>.data['data']['rain_delay']
"""

import logging

from collections import OrderedDict
import voluptuous as vol

from custom_components.opensprinkler import DATA_OPENSPRINKLER, DOMAIN
from datetime import datetime, timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import pytz

DEPENDENCIES = ['opensprinkler']

#DOMAIN = "opensprinkler"

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)

utc_tz = pytz.timezone('UTC')

# sensor_type [ description, unit, icon ]
SENSOR_TYPES = {
    'opensprinkler_rain': ['os_rain', None, 'mdi:weather-rainy'],
    'opensprinkler_lastrun': ['os_lastrun', None, 'mdi:history'],
    'opensprinkler_pump': ['os_pump', None, 'mdi:water-pump'],
    'opensprinkler_station': ['os_station', None, 'mdi:leaf'],
    'opensprinkler_schedule': ['os_schedule', None, 'mdi:calendar-clock']
}
SENSOR_TYPES_DEFAULT = {
    'opensprinkler_rain': ['os_rain', None, 'mdi:weather-rainy'],
    'opensprinkler_lastrun': ['os_lastrun', None, 'mdi:history'],
    'opensprinkler_pump': ['os_pump', None, 'mdi:water-pump'],
    'opensprinkler_station': ['os_station', None, 'mdi:leaf'],
    'opensprinkler_schedule': ['os_schedule', None, 'mdi:calendar-clock']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES_DEFAULT)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    osData = hass.data[DATA_OPENSPRINKLER]

    osData.update()
    schedules = osData.data['data']['programs']
    stations = osData.data['data']['stations']
    #settings = osData.data['data']['settings']
    #options = osData.data['data']['options']
    pump1 = osData.data['data']['pump1_index']
    pump2 = osData.data['data']['pump2_index']

    #_LOGGER.warning("stations: %s", stations)
    #_LOGGER.warning("schedules: %s", schedules)
    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        if (sensor_type == 'opensprinkler_schedule'):
            count = 1
            for sched in schedules:
                sensors.append(OpenSprinklerSensor(osData, sched, count, sensor_type))
                count += 1
        elif (sensor_type == 'opensprinkler_station'):
            count = 1
            for sta in stations:
                if (int(pump1)==count ):
                    sensors.append(OpenSprinklerSensor(osData, sta, 1, 'opensprinkler_pump'))

                elif (int(pump2)==count ):
                    sensors.append(OpenSprinklerSensor(osData, sta, 2, 'opensprinkler_pump'))
                else:
                    sensors.append(OpenSprinklerSensor(osData, sta, count, sensor_type))
                count += 1

        else:
            sensors.append(OpenSprinklerSensor(osData, '', '', sensor_type))
    add_devices(sensors, True)


class OpenSprinklerSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, osData, key, count, sensor_type):
        """Initialize the sensor."""
        self._sensor_type = sensor_type
        self._osData = osData
        self._key = key
        self._count = count
        self._name = key
        if (sensor_type == 'opensprinkler_schedule' or sensor_type == 'opensprinkler_station' or sensor_type == 'opensprinkler_pump'):
            t = SENSOR_TYPES[self._sensor_type][0]+"_"+str(count)
            #_LOGGER.warning("t1: %s", t)
            self.entity_id = "sensor."+t
        else:
            t = SENSOR_TYPES[self._sensor_type][0]
            #_LOGGER.warning("t2: %s", t)
            self.entity_id = "sensor."+t
        self._icon = SENSOR_TYPES[self._sensor_type][2]
        self._unit_of_measurement = SENSOR_TYPES[self._sensor_type][1]
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return icon."""
        return self._icon

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._osData.update()

        if (self._sensor_type == 'opensprinkler_lastrun'):
            utcTime = datetime.fromtimestamp(self._osData.data['data']['lastrun']['endtime'], utc_tz)
            self._state = utcTime.strftime("%d/%m %H:%M")
        elif(self._sensor_type == 'opensprinkler_rain'):
            if(self._osData.data['data']['rain_delay']==1):
              self._state = 'Active'
            else:
              self._state = 'None'
        elif(self._sensor_type == 'opensprinkler_schedule'):
            if(self._osData.data['data']['programs'][self._key]['Enabled']=='1'):
                self._state = "Enabled"
            else:
                self._state = "Disabled"
        elif(self._sensor_type == 'opensprinkler_pump'):
            if(self._osData.data['data']['stations'][self._key]['status']==1):
                self._state = "Running"
            else:
                self._state = "Idle"
        elif(self._sensor_type == 'opensprinkler_station'):
            if(self._osData.data['data']['stations'][self._key]['status']==1):
              if(self._osData.data['data']['stations'][self._key]['p_status'][0]==99):
                self._state = "Running manual"
              elif(self._osData.data['data']['stations'][self._key]['p_status'][0]==254):
                self._state = "Running once prog."
              elif(self._osData.data['data']['stations'][self._key]['p_status'][0]==0):
                self._state = "Idle"
              else:
                self._state = "Running schedule"
            else:
              if(self._osData.data['data']['stations'][self._key]['p_status'][0]>0):
                self._state = "Waiting for run"
              else:
                self._state = "Idle"
        else:
            self._state = 'OpenSprinkler'
    @property
    #def state_attributes(self):
    def device_state_attributes(self):

        """Return other details about the sensor state."""
        #attrs = OrderedDict()
        attrs = {}

        if(self._sensor_type == 'opensprinkler_lastrun'):
            attrs['station'] = str(self._osData.data['data']['lastrun']['station'])
            attrs['duration'] = str(self._osData.data['data']['lastrun']['duration'])+"s"
            attrs['program'] = str(self._osData.data['data']['lastrun']['program'])
            attrs['friendly_name'] = "Last run"
        elif(self._sensor_type == 'opensprinkler_rain'):
            attrs['friendly_name'] = "Rain delay"
            utcTime = datetime.fromtimestamp(self._osData.data['data']['rain_delay_time'], utc_tz)
            attrs['custom_ui_state_card'] = 'state-card-custom-ui'
            if(self._osData.data['data']['rain_delay']==1):
              attrs['extra_data_template'] = "until "+utcTime.strftime("%d/%m %H:%M")
            else:
              attrs['extra_data_template'] = ''
        elif(self._sensor_type == 'opensprinkler_pump'):
            attrs['friendly_name'] = self._key
            attrs['pump start delay'] = str(self._osData.data['data']['stations'][self._key]['pump1_delay_on'])+"s"
            attrs['pump end delay'] = str(self._osData.data['data']['stations'][self._key]['pump1_delay_off'])+"s"
        elif(self._sensor_type == 'opensprinkler_schedule'):
            attrs['friendly_name'] = self._key
            attrs['water_durations'] = self._osData.data['data']['programs'][self._key]['water_durations']
            if(self._osData.data['data']['programs'][self._key]['Weather']=='1'):
                attrs['weather'] = 'true'
            else:
                attrs['weather'] = 'false'
            if(self._osData.data['data']['programs'][self._key]['restrictions']=='01'):
                attrs['restrictions'] = 'Odd day restriction'
            elif(self._osData.data['data']['programs'][self._key]['restrictions']=='10'):
                attrs['restrictions'] = 'Even day restriction'
            if(self._osData.data['data']['programs'][self._key]['schedule_type']=='WEEKDAYS'):
                attrs['weekdays'] = self._osData.data['data']['programs'][self._key]['weekdays']
            elif(self._osData.data['data']['programs'][self._key]['schedule_type']=='INTERVAL'):
                attrs['interval'] = self._osData.data['data']['programs'][self._key]['interval']

            if(self._osData.data['data']['programs'][self._key]['start_type']=='Fixed time'):
                attrs['start_times'] = self._osData.data['data']['programs'][self._key]['start_times']
            else:
                attrs['interval_times'] = self._osData.data['data']['programs'][self._key]['interval_times']

        elif(self._sensor_type == 'opensprinkler_station'):
            #_LOGGER.warning(" self._key: %s",  self._key)
            attrs['friendly_name'] = self._key
            attrs['custom_ui_state_card'] = 'state-card-custom-ui'
            if (self._osData.data['data']['stations'][self._key]['p_status'][1] == 0):
              attrs['extra_data_template'] = ''
            else:
              attrs['extra_data_template'] = str(self._osData.data['data']['stations'][self._key]['p_status'][1])+"s remaining"
            if(self._osData.data['data']['stations'][self._key]['disabled']==1):
                attrs['hidden'] = 'true'
            if(self._osData.data['data']['stations'][self._key]['ignore_rain']==1):
                attrs['ignore_rain'] = 'true'
            else:
                attrs['ignore_rain'] = 'false'
            if(self._osData.data['data']['stations'][self._key]['sequencial']==1):
                attrs['sequencial'] = 'true'
            else:
                attrs['sequencial'] = 'false'
            if(self._osData.data['data']['stations'][self._key]['pump1']==1):
                attrs['pump1'] = 'true'
            else:
                attrs['pump1'] = 'false'
            if(self._osData.data['data']['stations'][self._key]['pump2']==1):
                attrs['pump2'] = 'true'
            else:
                attrs['pump2'] = 'false'

        return attrs
