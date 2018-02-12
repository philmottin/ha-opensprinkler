# OpenSprinkler component for Home Assistant

My first attempt to create a custom component on Home Assistant.
support for monitoring:
- Rain delay status and time
- Stations and pumps
- Schedules
- Last run

Click on a sensor to show all the correspondent data (see screenshots)
Uses HA CUSTOM-UI for live display of water durations (see screenshots)

## NOTES
  - Im working on the controller components with switches / scripts / input_selects
  - Planning to integrate this parse [https://github.com/dethpickle/python-opensprinkler](https://github.com/dethpickle/python-opensprinkler)


## INSTALLATION
- Require Home Assistant CUSTOM-UI [https://github.com/andrey-git/home-assistant-custom-ui](https://github.com/andrey-git/home-assistant-custom-ui) installed
- The component already set state-card-custom-ui. No need to set in customizer.
- Copy `custom_components` folder contents to your home assistant `custom_components` folder


## CONFIGURATION

  in your configuration.yaml:
  ```yaml
  #custom-ui
  frontend:
    extra_html_url:
      - /local/custom_ui/state-card-custom-ui.html
    extra_html_url_es5:
      - /local/custom_ui/state-card-custom-ui-es5.html


  opensprinkler:
    host: '0.0.0.0'
    port: 8080
    password: 'passwd-md5-hash'
```


  in your sensor.yaml
  ```yaml
  - platform: opensprinkler
    monitored_conditions:
      - opensprinkler_station
      - opensprinkler_schedule
      - opensprinkler_lastrun
      - opensprinkler_rain
```

The component will hide any disabled station on the go.
  in your group.yaml
  ```yaml
  group_opensprinkler:
      name: 'Open Sprinkler'
      control: hidden
      entities:
        - sensor.os_lastrun
        - sensor.os_rain
        - sensor.os_schedule_1
        - sensor.os_schedule_2
        - sensor.os_schedule_3
        - sensor.os_schedule_4
          #continue with all your schedules
        - sensor.os_station_1
        - sensor.os_station_2
        - sensor.os_station_3
        - sensor.os_station_4
        - sensor.os_station_5
        - sensor.os_station_6
        - sensor.os_station_7
        - sensor.os_station_8
        - sensor.os_pump_1
        - sensor.os_pump_2
```


## Screenshots
![pic1](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os1.JPG)
![pic2](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os2.JPG)
![pic3](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_prog1.JPG)
![pic4](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_prog2.JPG)
![pic5](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_station.JPG)
![pic6](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_pump.JPG)
![pic7](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_last_run.JPG)
