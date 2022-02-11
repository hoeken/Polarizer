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

def legend_polars():
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--legend', action='store', required=True)
	parser.add_argument('-s', '--sailset', action='store', required=True)

	args = parser.parse_args()

	polars = {}
	files = {}
	max_speed = boatpolar.BoatPolar()

	#did we get a real legend?
	if not os.path.isfile(args.legend):
		print "Legend file %s does not exist." % (args.legend)
		return False
	else:
		lfp = open(args.legend)
		legend_reader = csv.reader(lfp)

	#did we get a real sailset?
	if not os.path.isfile(args.sailset):
		print "Sailset file %s does not exist." % (args.sailset)
		return False
	else:
		sfp = open(args.sailset)
		sailset_reader = csv.reader(sfp)

	#load our files...
	i = 0
	for row in legend_reader:
		if i == 0:
			True
		else:
			category = row[0]
			filename = row[1]
			
			if not os.path.isfile(filename):
				print "Polar file %s does not exist." % (args.legend)
				return False
			else:
				files[category] = filename

				fp = open(filename, 'r')
				polars[category] = boatpolar.BoatPolar()
				polars[category].load_polar(fp)
		i += 1
			
	#now pull in numbers based on our sail config
	i = 0
	for row in sailset_reader:
		if i == 0:
			wind_speeds = row[1:]
		else:
			twa = row[0]
			sailset = row[1:]
			
			#pull in each rows values
			j = 0
			for tws in wind_speeds:
				my_sail = sailset[j]
				
				if my_sail:
					my_speed = polars[my_sail].get_speed(twa, tws)
					max_speed.set_speed(twa, tws, my_speed)
				j += 1
		i += 1
				
	#write our combined files
	max_speed.write_csv("polars/legend-polars-speed.csv")
	max_speed.write_predictwind("polars/legend-polars-predictwind.csv")
	
	print("Finished combining polars based on legend.")
			
if __name__ == '__main__':
	legend_polars()
    