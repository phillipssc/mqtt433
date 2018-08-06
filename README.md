# mqtt433
mqtt433 python service script to use rtl_433 and a SDR dongle to read Acurite temperature/humidity sensors (or other 433MHz) into JSON and publish to MQTT topic for Homeassistant sensor integration. I did not write the originals of these scripts, merely debugged for my own purposes.

The initially recommended way to get rtl_433 data into mosquitto is as follows:

rtl_433 -F json -U -R 30 | /usr/bin/mosquitto_pub -h <ip address> -u <login> -P <password> -t home/rtl_433 -l

The problem is that the sensors transmit each signal multiple times.   With two weather sensors and half a dozen contact sensors the system would get around a dozen messages per minute.   In the above command line that means a dozen logins per minute.  The system was unstable, mosquitto kept crashing.

Github member packitout did a great job of wrapping the process into a python script that allowed the login to mosquitto to be maintained between messages, this stopped the crashing.

I have taken this one step further.   For each sensor I get a signal from I store the value (minus the timestamp) for future comparison.  When new data comes in, I compare it against the old data and only send it if it has changed.   This makes it so that when a new value comes it - it will change something every time making sifting through logs much easier.

## mqtt433.py
this is the python script to run as a service. it requires paho-mqtt (https://pypi.python.org/pypi/paho-mqtt/1.1). Right now it only uses user authentication for the MQTT broker (so put the username and password you want this system to use to connect to the broker into this code) since it is meant to run on the hub machine connecting to the broker with the 1833 port (as opposed to the 8833 port for TLS encrypted traffic of MQTT clients outside the local network).

the line that defines "proc" specifies the rtl_433 call in the subprocess. In this example, the rtl_433 options are to output in JSON and only look for the two types of Acurite sensors I implemented. Use rtl_433 --help in the shell for more information.

It publishes to the topic "hass/rtl_433/sensor_0000" where 0000 is the sensor id number. This means you are not limited to the ABC channels on the Acurite tower sensors. They will have different id numbers so you can tell them apart. An easy way to find the id number is to either run rtl_433 in the shell to sniff their signals or use the commented line in mqtt433.py to publish any sensor output to the 'hass/rtl_433" MQTT topic and listen to that topic. Nice for debugging JSON outputs too.

## listener.py and publish.py
just used to listen or publish to MQTT topics for debugging.
