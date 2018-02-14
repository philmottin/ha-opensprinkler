# OpenSprinkler component for Home Assistant

My first attempt to create a custom component on Home Assistant.

### monitor:
Click on a sensor to show all the correspondent data (see screenshots)
Uses HA CUSTOM-UI for live display of water durations (see screenshots)
- Rain delay status and time
- Stations and pumps
- Schedules
- Last run

### controller:
Uses HA CUSTOM-UI for display buttons on custom states cards
- Manual run / stop stations
- Manual run programs

## NOTES
  - Planning to integrate this parse [https://github.com/dethpickle/python-opensprinkler](https://github.com/dethpickle/python-opensprinkler)
  - If you use this component, please give me your feedback. Im new to HA DEV enviroment and had to do few bad practices to acomplish the desire results. Here is some:
  - dummy input_text used as data transfer between custom ui state card and custom scene component
  - both controller state cards should be merged into one.
  - not sure if using scenes to handle all the controller's logic is the right way to do.


## INSTALLATION
- Require Home Assistant CUSTOM-UI [https://github.com/andrey-git/home-assistant-custom-ui](https://github.com/andrey-git/home-assistant-custom-ui) installed
- The component already set state-card-custom-ui. No need to set in customizer.
- Copy `custom_components` folder contents to your home assistant `custom_components` folder
- Copy both `www\custom_ui\custom state cards` to your home assistant `www\custom_ui\` folder


## CONFIGURATION
  in your configuration.yaml
  load the custom states cards
  ```yaml
  #custom-ui
  frontend:
    extra_html_url:
      - /local/custom_ui/state-card-custom-ui.html
      - /local/custom_ui/state-card-opensprinkler-control-station.html
      - /local/custom_ui/state-card-opensprinkler-control-program.html
    extra_html_url_es5:
      - /local/custom_ui/state-card-custom-ui-es5.html


  opensprinkler:
    host: '0.0.0.0'
    port: 8080
    password: 'passwd-md5-hash'
```


in your sensor.yaml
select the sensors to monitor
```yaml
- platform: opensprinkler
  monitored_conditions:
    - opensprinkler_station
    - opensprinkler_schedule
    - opensprinkler_lastrun
    - opensprinkler_rain
```

in your input_text.yaml
This is temporary solution, the controller needs to send data from custom ui to the custom scene component.
I couldn't figure out yet how to do this, so Im using this input_text as a workaround for now.  You can customize it with visible = 'true' so it doesn't show up.
```yaml
input_text:
  scene_temp_var:
    initial: 'off:1'
```


Add them all, the component will hide any disabled stations / programs.
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

  group_opensprinkler_controller:
      name: 'Open Sprinkler controller'
      control: hidden
      entities:
        - scene.os_program_1
        - scene.os_program_2
        - scene.os_program_3
        - scene.os_program_4
        #continue with all your schedules
        - scene.os_station_1
        - scene.os_station_2
        - scene.os_station_3
        - scene.os_station_4
        - scene.os_station_5
        - scene.os_station_6
        - scene.os_station_7
        - scene.os_station_8
```


## Screenshots
![pic1](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os1.JPG)
![pic2](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os2.JPG)
![pic3](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_controler.JPG)
![pic4](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_prog1.JPG)
![pic5](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_prog2.JPG)
![pic6](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_station.JPG)
![pic7](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_pump.JPG)
![pic8](https://raw.githubusercontent.com/philmottin/ha-opensprinkler/master/os_last_run.JPG)
