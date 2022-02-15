#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""load-predictwind-polars.py
Loads a predictwind polar file and writes it back out in our format.  Note: may not work since some predictwind polars have variable TWA/TWS pairs and interpolation is not implemented
"""

__author__ = "Zach Hoeken"
__copyright__ = "Copyright 2022, Zach Hoeken"
__credits__ = ["Zach Hoeken"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Zach Hoeken"
__email__ = "hoeken@gmail.com"
__status__ = "Beta"

import argparse
import os
import json
import datetime
import time
import numpy
import csv
import math
from pprint import pprint
import nmea0183
import boatpolar

def predictwind_polars():
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', action='store', required=True)

	args = parser.parse_args()
	
	output = boatpolar.BoatPolar()
	pw_polars = {}

	#did we get a real legend?
	if not os.path.isfile(args.file):
		print "Predictwind file %s does not exist." % (args.file)
		return False
	else:
		fp = open(args.file)
		reader = csv.reader(fp, dialect='excel-tab')

	#loop thru our predict wind file
	for row in reader:
		pw_tws = int(row[0])
		data = row[1:]
		
		#each line is TWS with TWA/BSP pairs:
		twa_lines = {}
		for i in range(len(data)/2):
			pw_twa = int(data[0+i*2])
			pw_bsp = float(data[1+i*2])
			
			twa_lines[pw_twa] = pw_bsp
			
		pw_polars[pw_tws] = twa_lines
		
	pprint(pw_polars)

	for my_tws in output.wind_speeds:
		if pw_polars.has_key(my_tws):
			twa_lines = pw_polars[my_tws]
			for my_twa in output.wind_angles:
				if twa_lines.has_key(my_twa):
					my_bsp = twa_lines[my_twa]
				else:
					#start = 0
					#end = output.wind_angles[0]

					#for i in range(len(output.wind_angles)-1):
					#	if pw_twa > output.wind_angles[i] and pw_twa < output.wind_angles[i+1]:
					#		start = output.wind_angles[i]
					#		end = output.wind_angles[i+1]
					#		break
						
				output.set_speed(my_twa, my_tws, my_bsp)

		#is this twa already in our list?
		#if pw_twa in output.wind_angles:
		#	my_bsp = pw_bsp
		#nope, figure out which one its between
		#else:
		#	start = 0
		#	end = output.wind_angles[0]

			#for i in range(len(output.wind_angles)-1):
			#	if pw_twa > output.wind_angles[i] and pw_twa < output.wind_angles[i+1]:
			#		start = output.wind_angles[i]
			#		end = output.wind_angles[i+1]
			#		break
					
		#	print ("{} {} {} {} {}".format(pw_tws, pw_twa, pw_bsp, start, end))
				
	#write our combined files
	output.write_csv("polars/predictwind-converted.csv")
	
	print("Finished loading Predictwind polars")
			
if __name__ == '__main__':
	predictwind_polars()
    