# mqtt433
mqtt433 python service script to use rtl_433 and a SDR dongle to read Acurite temperature/humidity sensors (or other 433MHz) into JSON and publish to MQTT topic for ~~Homeassistant~~ home automation sensor integration. I did not write the originals of these scripts, merely debugged for my own purposes.

The initially recommended way to get rtl_433 data into mosquitto is as follows:

rtl_433 -F json -U -G | /usr/bin/mosquitto_pub -h [ip address] -u [login] -P [password] -t home/rtl_433 -l

The problem is that the sensors transmit each signal multiple times.   With two weather sensors and half a dozen contact sensors the system would get around a dozen messages per minute.   In the above command line that means a dozen logins per minute.  The system was unstable, mosquitto kept crashing.

Github member packitout did a great job of wrapping the process into a python script that allowed the login to mosquitto to be maintained between messages, this stopped the crashing.

I have taken this one step further.   For each sensor I get a signal from I store the value (minus the timestamp) for future comparison.  When new data comes in, I compare it against the old data and only send it if it has changed.   This not only reduces data flow between the various programs but makes it so that when a new value comes in, it will not be the same value as last time making sifting through logs much less repetitive.  With this in place I get approximately 0 to 2 messages a minute.

## mqtt433.py
this is the python script to run as a service. it requires paho-mqtt (https://pypi.python.org/pypi/paho-mqtt/1.1). Right now it only uses user authentication for the MQTT broker (so put the username and password you want this system to use to connect to the broker into this code) since it is meant to run on the hub machine connecting to the broker with the 1833 port (as opposed to the 8833 port for TLS encrypted traffic of MQTT clients outside the local network).

## listener.py and publish.py
just used to listen or publish to MQTT topics for debugging.
