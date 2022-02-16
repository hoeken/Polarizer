#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Combine Polars
Combine various polar files into a single 'best of sailset' polar file.  Will generate speed polar, best sailset polar, sailset legend, and PredictWind polar.
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

def main():
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', action='store')
	parser.add_argument('-b', action='store')
	parser.add_argument('-c', action='store')
	parser.add_argument('-d', action='store')
	parser.add_argument('-e', action='store')
	parser.add_argument('-f', action='store')

	args = parser.parse_args()

	categories = {}
	files = {}

	legend = boatpolar.BoatPolar()
	max_speed = boatpolar.BoatPolar()
	best_vmg = boatpolar.BoatPolar()
	polars = {}
	
	#just hardcode in 6 configs cause we're lazy
	if args.a:
		categories['A'] = args.a
	if args.b:
		categories['B'] = args.b
	if args.c:
		categories['C'] = args.c
	if args.d:
		categories['D'] = args.d
	if args.e:
		categories['E'] = args.e
	if args.f:
		categories['F'] = args.f

	#use our categories to build a file list
	for key, val in categories.items():
		#files[key] = "polars/{}-median.csv".format(val)
		files[key] = "polars/{}-mean.csv".format(val)

	#make sure it exists
	for key, my_file in files.items():
		if not os.path.isfile(my_file):
			print ("Polar file %s does not exist." % (my_file))
			return False
		
		#load and parse our polar files...
		fp = open(my_file, 'r')
		polars[key] = boatpolar.BoatPolar()
		polars[key].load_polar(fp)

	#loop through each of our loaded polars.
	for key, polar in polars.items():
		#wind angle
		for twa in boatpolar.BoatPolar.wind_angles:
			#wind speed
			for tws in boatpolar.BoatPolar.wind_speeds:
				boat_speed = polar.get_speed(twa, tws)

				#did we get one?
				if boat_speed is not None:
					if boat_speed > 0:
						max_boat_speed = max_speed.get_speed(twa, tws)
						if not max_boat_speed or max_boat_speed < boat_speed:
							#save it to our legend and max speed
							legend.set_speed(twa, tws, key)
							max_speed.set_speed(twa, tws, boat_speed)
							
							#lets make a vmg one for kicks.
							if twa > 90:
								vmg = math.cos(math.radians(180 - twa)) * boat_speed
							else:
								vmg = math.cos(math.radians(twa)) * boat_speed
							vmg = round(vmg, 2)
							best_vmg.set_speed(twa, tws, vmg)
							
	#write our combined files
	legend.write_csv("polars/combined-polars-sailset.csv")
	max_speed.write_csv("polars/combined-polars-speed.csv")
	best_vmg.write_csv("polars/combined-polars-vmg.csv")
	max_speed.write_predictwind("polars/combined-polars-predictwind.txt")
	
	#show our max speed polars!
	max_speed.polar_chart()
	
	#save our legend file.
	fp = open("polars/combined-polars-legend.csv", 'w')
	csv_writer = csv.writer(fp)
	csv_writer.writerow(['ID', 'Filename'])
	keys = sorted(files.keys())
	for key in keys:
		my_file = files[key]
		csv_writer.writerow([key, my_file])
		
	print("Finished combining polars.")
			
if __name__ == '__main__':
	main()
    
