# wdrc-monitor
wdrc-monitor monitors the health of a wdrc over mqtt and checks for failure conditions such as timeouts. 
Built with python, PyQt6 for the GUI, and paho.mqtt as a message broker.

## Getting Started
Install Python

Install PyQt6

Install paho.mqtt

Install mosquitto broker

## Usage
### Config Files
#### app.json
The app.json config file contains the apps version number, name, organization, and theme.

#### health.json
The health.json config file contains information the HealthService uses to construct itself. The health.json and health_service.py are heavily linked together, deleting the first layer of keys will surely break the entire app. All values of the first layer keys should be dictionaries and link with objects defined in 'src.models'. 

The 'monitor' key is the config for all monitors attached to the health_service. A monitor contains montior entries which store a name, masks, and states. The masks tell us how to bit mask a value passed in when evaluating the state of an entry. Masks in health.json are a dictionary of mask to states (enum value), that way multiple masks can be applied on a single given entry. The name, color, dock, and hidden all refer to how the montior is created in the PyQt6 GUI, where name refers to the name of the dock or tab widget, the color for the entry names, the dock of which part of the screen to dock in ("left", "right", "top", "bottom", "center"), and hidden to hide the monitor on startup.

The 'heartbeats' key is the config for a type of timer class monitoring heartbeats sent by the wdrc. These are typically mqttping, which is a ping from a raspberry pi mosquitto broker and a ping which is the ping sent by the wdrc. The config file specifies the name, retry_limit, and time_limit. The name is the name of the heartbeat monitor and is used for displaying on the GUI. The retry_limit specifies how many times the heartbeat can fail consecutively (if message is on time will reset back to 0). The time_limit tells how long to wait to receive a heartbeat message, set a little higher than the expected time so mqtt has time to process the message.

The 'wdlms' key just tell use the name, color, and where to dock for the GUI.

#### mqtt.json