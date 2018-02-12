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
import requests
import json
import os
from collections import OrderedDict
from datetime import datetime, timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_PASSWORD)
from homeassistant.util import Throttle
from homeassistant.util import slugify
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.discovery import load_platform

#import homeassistant.components.input_select as input_select
from homeassistant.components.input_number import InputNumber

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=5)

# The domain of your component. Equal to the filename of your component.
DOMAIN = "opensprinkler"
DATA_OPENSPRINKLER = 'DATA_opensprinkler'
#OS_SELECT = "os_sectors"
weekDays = ['M','T','W','T','F','S','S']


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Setup the opensprinkler component."""
    # States are in the format DOMAIN.OBJECT_ID.
    conf = config[DOMAIN]
    server = conf.get(CONF_HOST)
    port = conf.get(CONF_PORT)
    password = conf.get(CONF_PASSWORD)

    server += ":"+port
    hass.data[DATA_OPENSPRINKLER] = OpenSprinklerData(server, password)
    hass.data[DATA_OPENSPRINKLER].update()
    #stations = hass.data[DATA_OPENSPRINKLER].data['data']['stations']
    #schedules = hass.data[DATA_OPENSPRINKLER].data['data']['programs']
    #_LOGGER.warning("stations: %s", stations)


    #select_data = {"options": list(stations), "entity_id": "input_select.os_control_station"}
    #select_data2 = {"options": list(schedules), "entity_id": "input_select.os_control_schedule"}
    #hass.services.call(input_select.DOMAIN, input_select.SERVICE_SET_OPTIONS, select_data)
    #hass.services.call(input_select.DOMAIN, input_select.SERVICE_SET_OPTIONS, select_data2)

    #hass.states.set('opensprinkler.opensprinkler', r.text)

    # Return boolean to indicate that initialization was successfully.
    return True

class OpenSprinklerData(object):
    """Get OpenSprinkler data via API."""

    def __init__(self, srv, passwd):
        self.data = None
        self.url = 'http://'+str(srv)+'/ja?pw='+str(passwd)
        self.url_manual = 'http://'+str(srv)+'/cm?pw='+str(passwd)

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest data from TFL."""
        api_dict = OrderedDict()
        response = requests.get(self.url)
        #_LOGGER.warning("response: %s", response.text)
        if response.status_code != 200:
            _LOGGER.warning("Invalid response from API DATA")
        else:
            api_dict['data'] = parse_api_data(json.loads(response.text, object_pairs_hook=OrderedDict))

        self.data = api_dict


def processDurations(durations, stations):
  strDurations = ''
  for i in range(0, len(stations)):
    seconds = int(durations[i])
    if (seconds != 0):
      minutes = 0
      hours = 0
      if (seconds >= 60): #minutes
        minutes = int(seconds/60)
        seconds = seconds%60

        if (minutes >= 60): #hour
          hours = int(minutes/60)
          minutes = minutes%60

      if (hours == 0):
          hours = ''
      else:
          hours = str(hours)+"h "
      if (minutes == 0):
          minutes = ''
      else:
          minutes = str(minutes)+"\' "
      if (seconds == 0):
          seconds = ''
      else:
          seconds = str(seconds)+"\'\' "

      strDurations += (stations[i] +" "+hours+minutes+seconds+"| ")
  return (strDurations[:-2])

def processStarts(starts, type):
  strStarts = ''
  if (type == 'Fixed time'):
    for t in starts:
      if (t != -1):
        s_time = datetime.strptime('00:00', '%H:%M')
        s_time_adj = (s_time + timedelta(minutes=t)).strftime("%H:%M")
        strStarts += str(s_time_adj) +" | "
    return (strStarts[:-3])
  else:
    s_time = datetime.strptime('00:00', '%H:%M')
    s_time_adj = (s_time + timedelta(minutes=starts[0])).strftime("%H:%M")
    strStarts += str(s_time_adj) +" | "
    h = round(starts[2]/60)
    if (h == 1):
      strStarts += "every "+str(h) +" hour | "
    else:
      strStarts += "every "+str(h) +" hours | "
    if (starts[1] == 1):
      strStarts += str(starts[1]) +" time"
    else:
      strStarts += str(starts[1]) +" times"
    return (strStarts)

def processDays(d0,d1,type):
  strDays = ''
  if (type == 'WEEKDAYS'):
    i_bin = 7
    for i in range(0, len(d0)-1):
      if (d0[i_bin]=='1'):
        strDays += weekDays[i]
      else:
        strDays += ' - '
      if (i < 6):
        strDays += ' | '
      i_bin-=1
  else:
    if (d1 == 1):
      strDays = '1 day interval'
    else:
      strDays = str(d1)+' days interval'
  return (strDays)

def processLastRun(lrun, stations):
    dictLastRun = OrderedDict()
    dictLastRun['stationIndex'] = lrun[0]
    dictLastRun['station'] = stations[lrun[0]]
    dictLastRun['progIndex'] = lrun[1]
    if(lrun[1]==99):
      dictLastRun['program'] = "Manual run"
    elif(lrun[1]==254):
      dictLastRun['program'] = "Run once prog."
    else:
      dictLastRun['program'] = "Schedule run"

    dictLastRun['duration'] = lrun[2]
    dictLastRun['endtime'] = lrun[3]
    return (dictLastRun)

def parse_api_data(response):

    programs = response['programs']['pd']
    settings = response['settings']
    options = response['options']
    stations = response['stations']

    ignore_rain = str(bin(stations['ignore_rain'][0]))[2:]
    if (len(ignore_rain) < 8):
        missing = 8-len(ignore_rain)
        for i in range(missing):
            ignore_rain = "0"+ignore_rain

    disabled = str(bin(stations['stn_dis'][0]))[2:]
    if (len(disabled) < 8):
        missing = 8-len(disabled)
        for i in range(missing):
            disabled = "0"+disabled

    sequencial = str(bin(stations['stn_seq'][0]))[2:]
    if (len(sequencial) < 8):
        missing = 8-len(sequencial)
        for i in range(missing):
            sequencial = "0"+sequencial

    pump1 = str(bin(stations['masop'][0]))[2:]
    if (len(pump1) < 8):
        missing = 8-len(pump1)
        for i in range(missing):
            pump1 = "0"+pump1

    pump2 = str(bin(stations['masop2'][0]))[2:]
    if (len(pump2) < 8):
        missing = 8-len(pump2)
        for i in range(missing):
            pump2 = "0"+pump2

    sbits = str(bin(settings['sbits'][0]))[2:]
    if (len(sbits) < 8):
        missing = 8-len(sbits)
        for i in range(missing):
            sbits = "0"+sbits

    p_status = settings['ps']
    rain_delay = settings['rd']
    rain_delay_time = settings['rdst']

    pump1_index = options['mas']
    pump1_delay_on = options['mton']
    pump1_delay_off = options['mtof']
    pump2_index = options['mas2']
    pump2_delay_on = options['mton2']
    pump2_delay_off = options['mtof2']

    my_dict = OrderedDict()
    my_dict['stations'] = OrderedDict()
    my_dict['pump1_index'] = pump1_index
    my_dict['pump2_index'] = pump2_index

    my_dict['rain_delay'] = rain_delay
    my_dict['rain_delay_time'] = rain_delay_time
    my_dict['lastrun'] = processLastRun(settings['lrun'], stations['snames'])
    my_dict['snames'] = stations['snames']
    i = 0
    i_bin = (7)
    while (i<=7):
    #for sta in stations['snames']:
        sta = stations['snames'][i]
        settings_dict = OrderedDict()
        settings_dict['name'] = sta
        settings_dict['disabled'] = int(disabled[i_bin])
        settings_dict['ignore_rain'] = int(ignore_rain[i_bin])
        settings_dict['sequencial'] = int(sequencial[i_bin])
        settings_dict['pump1'] = int(pump1[i_bin])
        settings_dict['pump2'] = int(pump2[i_bin])
        settings_dict['status'] = int(sbits[i_bin])
        settings_dict['index'] = i
        settings_dict['p_status'] = p_status[i]
        if ((i+1)==int(pump1_index)):
          settings_dict['pump1_delay_on'] = pump1_delay_on
          settings_dict['pump1_delay_off'] = pump1_delay_off
        elif ((i+1)==int(pump2_index)):
          settings_dict['pump2_delay_on'] = pump2_delay_on
          settings_dict['pump2_delay_off'] = pump2_delay_off

        my_dict['stations'][sta] = settings_dict
        i_bin -= 1
        i += 1

    i=0
    my_dict['programs'] = OrderedDict()
    #_LOGGER.warning("programs: %s", str(programs))

    for prog in programs:
        settings_dict = OrderedDict()

        days0 = prog[1]
        days1 = prog[2]
        starts = prog[3]
        durations = prog[4]
        name = prog[5]

        flags = str(bin(prog[0]))[2:]
        if (len(flags) < 8):
            missing = 8-len(flags)
            for i in range(missing):
                flags = "0"+flags

        settings_dict['Enabled'] = flags[7]
        settings_dict['Weather'] = flags[6]
        settings_dict['restrictions'] = flags[5]+str(flags[4])

        if (flags[3]=='0' and flags[2]=='0'):
            settings_dict['weekdays'] = processDays(format(days0, '08b'),format(days1, '08b'),'WEEKDAYS')
            settings_dict['schedule_type'] = 'WEEKDAYS'
        else:
            settings_dict['interval'] = processDays(days0, days1,'INTERVAL')
            settings_dict['schedule_type'] = 'INTERVAL'

        if (flags[1]=='1'):
            settings_dict['start_type'] = 'Fixed time'
            settings_dict['start_times'] = processStarts(starts, 'Fixed time')
        else:
            settings_dict['start_type'] = 'Repeating time'
            settings_dict['interval_times'] = processStarts(starts, 'Repeating time')

        settings_dict['water_durations'] = processDurations(durations,stations['snames'])

        settings_dict['index'] = i
        settings_dict['name'] = name
        settings_dict['flags'] = flags
        settings_dict['days0'] = days0
        settings_dict['days1'] = days1
        settings_dict['starts'] = starts
        settings_dict['durations'] = durations

        my_dict['programs'][name] = settings_dict
        i += 1

    return my_dict
