"""
 OpenSprinkler custom component for Home Assistant

 Author: Phil Mottin
 Version: 1.1
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
import string
from custom_components.opensprinkler import DOMAIN, DATA_OPENSPRINKLER
from homeassistant.components.scene import Scene
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
  osData = hass.data[DATA_OPENSPRINKLER]

  osData.update()
  schedules = osData.data['data']['programs']
  stations = osData.data['data']['stations']
  # settings = osData.data['data']['settings']
  # options = osData.data['data']['options']
  pump1 = osData.data['data']['pump1_index']
  pump2 = osData.data['data']['pump2_index']

  # _LOGGER.warning("stations: %s", stations)
  # _LOGGER.warning("schedules: %s", schedules)
  scenes = []

  count = 1
  for program in schedules:
    scenes.append(ProgramScene(program, hass.states, count,'program', osData))
    count += 1

  count = 1
  for station in stations:
    if( (int(pump1) != count) and (int(pump2) != count) ):
        scenes.append(ProgramScene(station, hass.states, count, 'station',osData))
    count += 1

  add_devices(scenes, True)


class ProgramScene(Scene):

  def __init__(self, name, states, count, type, osData):
    self._states = states
    self._name = name
    self._osData = osData
    self._type = type
    self._index = count-1
    self.entity_id = "scene.os_"+type+"_" + str(count)

    if (self._type == 'station'):
      self._icon = 'mdi:leaf'
    elif (self._type == 'program'):
      self._icon = 'mdi:calendar-clock'

  @property
  def name(self):
    """Return the name of the binary sensor."""
    return self._name

  @property
  def icon(self):
    """Return icon."""
    return self._icon

  @property
  def should_poll(self):
    """Return that polling is not necessary."""
    return False

  def activate(self, **kwargs):
    """Turn the device on."""
    if (self._type == 'station'):
      value = self._states.get('input_text.scene_temp_var').state.split(':')
      command = value[0]
      mins = int(value[1].split('.')[0])*60
      if (command == 'on'):
        self._osData.turn_on(mins,self._name)
      elif (command == 'off'):
        self._osData.turn_off(self._name)
    elif (self._type == 'program'):
      self._osData.activate(self._index)

  @property
  #def state_attributes(self):
  def device_state_attributes(self):

    """Return other details about the sensor state."""
    # attrs = OrderedDict()
    attrs = {}

    if (self._type == 'station'):
      attrs['custom_ui_state_card'] = 'state-card-opensprinkler-control-station'
      if(self._osData.data['data']['stations'][self._name]['disabled']==1):
        attrs['hidden'] = 'true'

    elif (self._type == 'program'):
      attrs['custom_ui_state_card'] = 'state-card-opensprinkler-control-program'

    return attrs
