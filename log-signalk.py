#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Log SignalK data over IP
The logging script that will connect to a Signal K server and log the data to a file.
"""

__author__ = "Zach Hoeken"
__copyright__ = "Copyright 2022, Zach Hoeken"
__credits__ = ["Zach Hoeken"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Zach Hoeken"
__email__ = "hoeken@gmail.com"
__status__ = "Beta"

import time
import pprint
import datetime
import tzlocal
import json
import argparse
import os
from pprint import pprint
import websocket
import math

def on_message(wsapp, message):
	print(message)

def main():
    
	#these are our command line arguments
	parser = argparse.ArgumentParser(description='Log SignalK data from a server to a text file.')
	parser.add_argument('-i', '--ip', action='store', default='192.168.50.20', help='IP Address of the NMEA0183 server')
	parser.add_argument('-p', '--port', action='store', default='10110', help='Port of the NMEA0183 server')
	parser.add_argument('-c', '--config', action='store', default='default', help='Sail configuration.  Can be any arbitrary text.  eg. "jib and main", "spinnaker", etc.')
    
	args = parser.parse_args()
	
	#generate our filename
	d = datetime.datetime.today()
	now = d.strftime("%Y-%m-%d %H%M")
	fname = "data/{}/signalk-log-{}-{}.txt".format(args.config, args.config, now)

	#does our directory exist?
	if not os.path.exists("data"):
		os.mkdir("data")
	if not os.path.exists("data/{}".format(args.config)):
		os.mkdir("data/{}".format(args.config))

	#connect to our signalk server
	ws = websocket.WebSocket()
	ws.connect("ws://boatpi.local/signalk/v1/stream?subscribe=none")
	server_data = json.loads(ws.recv())

	#we only want to get a few data points
	request = """
		{
			"context": "vessels.self",
			"subscribe": [
				{
					"path": "environment.wind.angleTrueWater",
					"period": 1000,
					"format": "delta",
					"policy": "instant",
					"minPeriod": 200
				},
				{
					"path": "environment.wind.speedTrue",
					"period": 1000,
					"format": "delta",
					"policy": "instant",
					"minPeriod": 200
				},
				{
					"path": "navigation.speedOverGround",
					"period": 1000,
					"format": "delta",
					"policy": "instant",
					"minPeriod": 200
				},
				{
					"path": "navigation.speedThroughWater",
					"period": 1000,
					"format": "delta",
					"policy": "instant",
					"minPeriod": 200
				}
			]
		}
	"""
	ws.send(request)

	with open(fname, 'w') as f:
		try:
			#log forever
			while True:
			
				line = ws.recv()
				output = json.loads(line)

				#pprint(output)
			
				#write our line to our file...
				jdata = {}
				jdata['time'] = datetime.datetime.now().isoformat()
				jdata['unix_time'] = time.time()
				jdata['timezone'] = str(tzlocal.get_localzone())
				jdata['source'] = 'signalk'
				jdata['lines'] = line
				f.write(json.dumps(jdata) + "\n")
			
				path = output['updates'][0]['values'][0]['path']
				value = float(output['updates'][0]['values'][0]['value'])

				#is it a known code?
				#TWA - environment.wind.angleTrueWater
				#TWS - environment.wind.speedTrue
				#SOG - navigation.speedOverGround
				#BSP - navigation.speedThroughWater
				
				if path == 'navigation.speedOverGround':
					sog = round(value * 1.94384, 1)
					print('SOG: {}'.format(sog))
				if path == 'navigation.speedThroughWater':
					bsp = round(value * 1.94384, 1)
					print('BSP: {}'.format(bsp))
				if path == 'environment.wind.speedTrue':
					tws = round(value * 1.94384, 1)
					print('TWS: {}'.format(tws))
				if path == 'environment.wind.angleTrueWater':
					twa = round(math.degrees(value))
					print('TWA: {}'.format(twa))
					
		except KeyboardInterrupt:
			print("Exiting.")
		except Exception as e:
			pprint(e)

	#clean up our socket
	ws.close()
		
if __name__ == '__main__':
	main()
