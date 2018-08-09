#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import paho.mqtt.client as mqtt
import logging
import subprocess
import copy
import threading
import argparse

parser = argparse.ArgumentParser(description='Cache incoming rtl_433 radio messages and surpress duplicates')
parser.add_argument('--nocache', nargs='*', help='ids of devices not to cache and therefore allow every message to pass')
parser.add_argument('--tmpcache', nargs='*', help='ids of devices to cache for only a couple of seconds and therefore allow some messages to get filtered')
args = parser.parse_args()

def on_connect(client, userdata, flags, rc):
    logging.info("CNNACK received with code %d." % (rc))

def on_publish(client, userdata, mid):
    logging.info("mid: "+str(mid))

#logging.basicConfig(filename=__file__.replace(".py",'.log'),level=logging.INFO)
logging.basicConfig(filename="/var/log/mqtt433.log",level=logging.INFO)
logging.info("start")

mqttc = mqtt.Client("python_pub")
mqttc.username_pw_set(username="<LOGIN>", password="<PASSWORD>")
mqttc.connect("localhost", port=1883)
mqttc.loop_start()
logging.info("main loop")

proc = subprocess.Popen(['rtl_433', '-F', 'json', '-R', '12', '-R', '30', '-R', '40'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#proc = subprocess.Popen(['rtl_433', '-F', 'json', '-G'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

linedata = {}

def killcachedid(arg):
    linedata.pop(arg, None)

while True:
    try:
        logging.debug("listening")
        input = proc.stdout.readline()
        payload = json.loads(input.decode("utf-8"))
        # Make a copy for manipulaqtion
        payload_nt = copy.copy(payload)
        # Remove the time component (as it will often be the only changing value)        
        payload_nt.pop('time')
        logging.debug(json.dumps(payload_nt))
        # Get the key for the storage dictionary
        id = payload_nt['id']
        logging.debug("id: " + str(id))
        olddata = ""
        # If we have previously stored data for this - load it into olddata
        if id in linedata:
            olddata = linedata[id]
        logging.debug("old: "+json.dumps(olddata))
        # If the data has changed for this id (other than time) send it (the original data) out
        if payload_nt != olddata:
            # publish the delta for the specific sensor
            for key, value in payload_nt.items():
                if olddata == "" or value != olddata[key]:
                    (rc, mid) = mqttc.publish("r433/" + str(id) + "/" + key, value)
            # Store the latest time-free data in the dictionary for this id
            if args.nocache is None or args.nocache is not None and str(id) not in args.nocache:
                linedata[id] = payload_nt
                logging.debug("cached id " + str(id) + " as: " + json.dumps(payload_nt))
            if args.tmpcache is not None and str(id) in args.tmpcache:
                t = threading.Timer(2, killcachedid, [id])
                t.start()
    except Exception as x:
        logging.warning("exception %s" % x)
        logging.warning("input:'%s'" % input)
    except KeyboardInterrupt:
        sys.stdout.flush()
        logging.warning("exit")
        break
