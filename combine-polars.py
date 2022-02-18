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
	parser = argparse.ArgumentParser(description='Combine multiple polars into a single "best of sailset" polar.')
	parser.add_argument('-a', action='store', help="Sailset A. Must correspond to sailset name from logging and generation.")
	parser.add_argument('-b', action='store', help="Sailset B. Must correspond to sailset name from logging and generation.")
	parser.add_argument('-c', action='store', help="Sailset C. Must correspond to sailset name from logging and generation.")
	parser.add_argument('-d', action='store', help="Sailset D. Must correspond to sailset name from logging and generation.")
	parser.add_argument('-e', action='store', help="Sailset E. Must correspond to sailset name from logging and generation.")
	parser.add_argument('-f', action='store', help="Sailset F. Must correspond to sailset name from logging and generation.")
	parser.add_argument('-g', '--graph', default=False, action='store_true', help="Show interactive polar chart graph.")
	parser.add_argument('--name', default=None, action='store', help="Name of your boat")
		
	args = parser.parse_args()

	categories = {}
	files = {}

	legend = boatpolar.BoatPolar()
	max_speed = boatpolar.BoatPolar()
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

	#generate our vmg too
	best_vmg = max_speed.calculate_vmg()
							
	#write our combined files
	legend.write_csv("polars/combined-polars-sailset.csv")
	max_speed.write_csv("polars/combined-polars-speed.csv")
	max_speed.write_predictwind("polars/combined-polars-predictwind.txt")
	best_vmg.write_csv("polars/combined-polars-vmg.csv")
	
	#show our max speed polars!
	if args.name:
		title = "{} - Best Sailset Polar Chart".format(args.name)
	else:
		title = "Best Sailset Polar Chart".format(args.name)
	
	max_speed.polar_chart(args.graph, "graphs/combined-polar-chart.png", title)
	
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
    
