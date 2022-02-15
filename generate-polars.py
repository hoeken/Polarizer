#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate Polars
Parses NMEA0183 log files and generates polars.
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

from scipy import signal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', action='store')
	parser.add_argument('-d', '--dir', action='store')
	parser.add_argument('-p', '--polar', action='store')
	parser.add_argument('-g', '--graph', default=False, action='store_true')
	parser.add_argument('--twa_min', action='store', default = 0, type=float)
	parser.add_argument('--twa_max', action='store', default = 180, type=float)

	args = parser.parse_args()
	
	bp = boatpolar.BoatPolar()
	files = []
	polar_name = 'unknown'
	
	use_sog = False
	
	#our running avg since nmea0183 sucks
	running_avg_count = 10
	twa_list = []
	tws_list = []
	bsp_list = []
	wind_time = 0
	bsp_time = 0
	
	#this is for graphing... probably a better way to do this.
	tws_time = []
	tws_data = []
	tws_avg_time = []
	tws_avg_data = []
	
	#did we get a single file?
	if args.file:
		#make sure it exists
		if not os.path.isfile(args.file):
			print ("Log file %s does not exist." % (args.file))
			return False
		else:
			files.append(args.file)

		#try to make a good default
		parts = os.path.basename(args.file).split('.')
		polar_name = '.'.join(parts[0:-1])

	#a directory of files?
	elif args.dir:
		if not os.path.exists(args.dir):
			print ("Director %s does not exist." % (args.dir))
			return False

		#use our directory name
		path = os.path.normpath(args.dir)
		polar_name = os.path.basename(path)
		dirfiles = os.listdir(path)
		for fname in dirfiles:
			files.append(os.path.join(path, fname))
		
		if len(files) == 0:
			print ("No files found in {}".format(path))
			return False

	#what is our 'category' for polar data
	if args.polar:
		polar_name = args.polar
		
	#loop through all our data files
	for myfile in files:

		#open our file for reading
		print("Parsing file {}".format(myfile))
		fp = open(myfile)
		while True:

			#read lines until the end of file.
			json_line = fp.readline()
			if json_line == '':
				break;
			
			try:
				data = json.loads(json_line)
			except ValueError as e:
				continue
			
			#did we get any data?
			if data['lines'] is not None:
				for line in data['lines']:

					# run it through our parser
					nmea = nmea0183.nmea0183()
					output = nmea.parseline(line)
				
					#lets only parse valid strings
					if not nmea.valid:
						#print(line)
						continue

					#is it a known code?
					if not nmea.known:
						#pprint(output)
						continue
						
					#when did we record this?
					output['time'] = data['time']

					#oh sweet sweet unix epoch
					if 'unix_time' in data:
						unix_time = data['unix_time']
					#fucking date times.... old log entries didnt have the unix_time variable
					else:
						ts = datetime.datetime.strptime(output['time'][0:19], "%Y-%m-%dT%H:%M:%S")
						unix_time = time.mktime(ts.timetuple())
						micros = output['time'][19:]
						if micros != '':
							micros = float(micros)
						else:
							micros = 0.0
						unix_time += micros

					#wind speed...
					if 'tws' in output and 'twa' in output:
						twa = float(output['twa'])
						tws = float(output['tws'])
						if (twa < args.twa_min):
							print("Less than {} TWA ({}) at {}".format(args.twa_min, twa, output['time']))
							continue
						if (twa > args.twa_max):
							print("Greater than {} TWA ({}) at {}".format(args.twa_max, twa, output['time']))
							continue
							
						twa_list.append(twa)
						tws_list.append(tws)
						wind_time = unix_time
						
						tws_time.append(datetime.datetime.fromtimestamp(unix_time))
						tws_data.append(tws)
							
					#boat speed... use SOG
					if use_sog:
						if 'sog' in output and nmea.sentence == 'RMC' and output['sog']:
							bsp = float(output['sog'])
							bsp_list.append(bsp)
							bsp_time = unix_time
					else:
						if 'water_speed' in output and nmea.sentence == 'VHW' and output['water_speed']:
							bsp = float(output['water_speed'])
							bsp_list.append(bsp)
							bsp_time = unix_time

					#limit our running average arrays
					while len(twa_list) > running_avg_count:
						twa_list.pop(0)
					while len(tws_list) > running_avg_count:
						tws_list.pop(0)
					while len(bsp_list) > running_avg_count:
						bsp_list.pop(0)

					#add this to the list...
					time_delta = abs(wind_time - bsp_time)
					if wind_time > 0 and bsp_time > 0 and time_delta <= 1:
						avg_twa = numpy.average(twa_list)
						avg_tws = numpy.average(tws_list)
						avg_bsp = numpy.average(bsp_list)
						
						tws_avg_time.append(datetime.datetime.fromtimestamp(wind_time))
						tws_avg_data.append(round(avg_tws, 2))

						print("TWA: {} TWS: {} BSP: {}".format(round(avg_twa), round(avg_tws, 2), round(avg_bsp, 2)))

						bp.bin_speeds(avg_twa, avg_tws, avg_bsp)
						
						wind_time = 0
						bsp_time = 0
			else:
				print ("Empty lines...")

		fp.close()		

	#cruncho el numero
	all_polars = bp.generate_polars()
	
	#write our files...
	for idx, polar in all_polars.items():
		fname = "polars/{}-{}.csv".format(polar_name, idx)
		print("Writing results to {}".format(fname))
		polar.write_csv(fname)

	#Pandas Test Zone!
	if args.graph:
		tws_index = pd.DatetimeIndex(tws_time)
		tws_df = pd.DataFrame({'time': tws_index, 'tws': tws_data}, index=tws_index)

		tws_avg_index = pd.DatetimeIndex(tws_avg_time)
		tws_avg_df = pd.DataFrame({'time': tws_avg_index, 'tws': tws_avg_data}, index=tws_avg_index)

		print(tws_df)
		print(tws_avg_df)

		x = tws_df['time']
		y = tws_df['tws']
		plt.scatter(x, y, s=1, c='orange', label='Raw')

		x = tws_avg_df['time']
		y = tws_avg_df['tws']
		plt.plot(x, y, c='royalblue', label='Average')
		#plt.xlabel('Time')
		#plt.ylabel('TWS')

		b, a = signal.ellip(4, 0.01, 120, 0.125)  # Filter to be applied.
		fgust = signal.filtfilt(b, a, tws_df['tws'], method="gust")
		#plt.plot(x, fgust[0:len(x)], c='red', label='FiltFilt')

		b, a = signal.ellip(8, 0.01, 120, 0.125)  # Filter to be applied.
		fgust = signal.filtfilt(b, a, tws_df['tws'], method="gust")
		#plt.plot(x, fgust[0:len(x)], c='green', label='FiltFilt8')

		b, a = signal.ellip(10, 0.01, 120, 0.125)  # Filter to be applied.
		fgust = signal.filtfilt(b, a, tws_df['tws'], method="gust")
		plt.plot(x, fgust[0:len(x)], c='purple', label='FiltFilt10')

		ax = plt.gca()
		ax.set_ylim([0, None])

		plt.xlabel('Time')
		plt.ylabel('TWS')
		plt.legend()
		plt.show()

if __name__ == '__main__':
	main()
    
