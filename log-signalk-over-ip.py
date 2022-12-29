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

def on_message(wsapp, message):
	print(message)

def main():
    
	#these are our command line arguments
	parser = argparse.ArgumentParser(description='Log NMEA0183 data from a server to a text file.')
	parser.add_argument('-i', '--ip', action='store', default='192.168.50.20', help='IP Address of the NMEA0183 server')
	parser.add_argument('-p', '--port', action='store', default='10110', help='Port of the NMEA0183 server')
	parser.add_argument('-c', '--config', action='store', default='default', help='Sail configuration.  Can be any arbitrary text.  eg. "jib and main", "spinnaker", etc.')
    
	args = parser.parse_args()

	#TWA - environment.wind.angleTrueWater
	#TWS - environment.wind.speedTrue
	#SOG - navigation.speedOverGround
	#BSP - navigation.speedThroughWater
	
	#connect to our signalk server
	#wsapp = websocket.WebSocket("ws://boatpi.local/signalk/v1/stream?subscribe=none", on_message=on_message)
	#wsapp.send(request)
	#wsapp.run_forever()
	
	ws = websocket.WebSocket()
	ws.connect("ws://boatpi.local/signalk/v1/stream?subscribe=none")

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

	while(True):
		print(json.loads(ws.recv()))
	
	return True
	
	#generate our filename
	d = datetime.datetime.today()
	now = d.strftime("%Y-%m-%d %H%M")
	fname = "data/{}/nmea0183-log-{}-{}.txt".format(args.config, args.config, now)

	#does our directory exist?
	if not os.path.exists("data/{}".format(args.config)):
		os.mkdir("data/{}".format(args.config))

	#init our data
	line = ''
	nmea = nmea0183.nmea0183()

	#start our log file
	with open(fname, 'w') as f:
		try:
			#log forever
			while True:
				
				#get data from the receiver
				line += s.recv(1)
				
				#did we get a new line?
				if line[-2:] == '\r\n':
					
					#is it a valid nmea0183 line?
					output = nmea.parseline(line)
					if nmea.valid:
						
						#write our line to our file...
						jdata = {}
						jdata['time'] = datetime.datetime.now().isoformat()
						jdata['unix_time'] = time.time()
						jdata['timezone'] = str(tzlocal.get_localzone())
						jdata['lines'] = [line[0:-2]]
						f.write(json.dumps(jdata) + "\n")
						
						#is it a known code?
						if output.has_key('sog') and nmea.sentence == 'RMC':
							print('[{}] SOG: {}'.format(nmea.sentence, output['sog']))
						if output.has_key('water_speed') and nmea.sentence == 'VHW':
							print('[{}] BSP: {}'.format(nmea.sentence, output['water_speed']))
						if output.has_key('twa'):
							print('[{}] TWA: {} TWS: {}'.format(nmea.sentence, output['twa'], output['tws']))
					
					#reset our buffer
					line = ''
				
		except Exception as e:
			pprint(e)

	#clean up our socket
	s.close()
		
if __name__ == '__main__':
	main()
