#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""tester
Basic test script that connects to a NMEA0183 server and reads data
"""

__author__ = "Zach Hoeken"
__copyright__ = "Copyright 2022, Zach Hoeken"
__credits__ = ["Zach Hoeken"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Zach Hoeken"
__email__ = "hoeken@gmail.com"
__status__ = "Beta"

import socket, time
import pprint
import datetime
import json
import argparse
import os
import nmea0183
import numpy
from pprint import pprint

def listener():
    
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--ip', action='store', default='192.168.50.20')
	parser.add_argument('-p', '--port', action='store', default='10110')
    
	args = parser.parse_args()

	#connect to our socket
	s = socket.socket()
	s.connect((args.ip, int(args.port)))

	#init our data
	line = ''
	nmea = nmea0183.nmea0183()

	#log forever
	while True:
		#get data from the receiver
		line += s.recv(1)
		
		#did we get a new line?
		if line[-2:] == '\r\n':
			#is it a valid nmea0183 line?
			line = line.strip()
			output = nmea.parseline(line)
			if nmea.valid:
				if nmea.sentence == 'VHW':
					boat_speed = output['water_speed']
					print("Boat Speed: {}".format(boat_speed))
				elif nmea.sentence == 'RMC':
					sog = output['sog']
					print("SOG: {}".format(sog))
				#is it a known code?
				elif not nmea.known:
					print(line)
					pprint(nmea.params)
			#else:
			#	pprint(line)

			#reset our buffer
			line = ''

	#clean up our socket
	s.close()
		
if __name__ == '__main__':
	listener()