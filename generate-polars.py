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
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def main():
	#these are our command line arguments
	parser = argparse.ArgumentParser(description='Parse a NMEA0183 log file and generate polars.')
	parser.add_argument('-f', '--file', action='store', help='Filename to parse, for parsing individual files, usually for debug.')
	parser.add_argument('-p', '--polar', action='store', help='Sailset configuration name. Not needed if parsing a directory.')
	parser.add_argument('-d', '--dir', action='store', help='Directory to parse.  Will use name of directory as sailset configuration name.')
	parser.add_argument('-g', '--graph', default=False, action='store_true', help="Show interactive graph. Will always automatically generate .png graph images.")
	parser.add_argument('--filter', default='butter', help="What kind of filter to use. 'rolling' = Rolling average.  'butter' = Butterworth filter. 'none' = No Filter.")
	parser.add_argument('--filter_seconds', default=10, type=int, help="How many seconds for the rolling filter. Default is 10s")
	parser.add_argument('--filter_hz', default=0.10, type=float, help="What hz to use for the Butterworth filter.  Default is 0.1hz.  Lower is smoother")
	parser.add_argument('--twa_min', action='store', default = 0, type=int, help="Minimum TWA to generate polars for, inclusive")
	parser.add_argument('--twa_max', action='store', default = 180, type=int, help="Maximum TWA to generate polars for, inclusive.")
	parser.add_argument('--tws_min', action='store', default = 0, type=int, help="Minimum TWS to generate polars for, inclusive")
	parser.add_argument('--tws_max', action='store', default = 35, type=int, help="Maximum TWS to generate polars for, inclusive.")

	args = parser.parse_args()
	
	bp = boatpolar.BoatPolar()
	files = []
	polar_name = 'unknown'
	
	total_points = 0
	
	use_sog = False
	
	#our running avg since nmea0183 sucks
	running_avg_count = 10
	
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
			if fname.endswith('.txt'):
				files.append(os.path.join(path, fname))
		
		if len(files) == 0:
			print ("No files found in {}".format(path))
			return False

	#what is our 'category' for polar data
	if args.polar:
		polar_name = args.polar

	#what is our maximum boat speed we saw?
	max_bsp = 0
		
	#loop through all our data files
	for myfile in files:
		#our arrays
		twa_data = []
		tws_data = []
		bsp_data = []
		
		twa_time = []
		tws_time = []
		bsp_time = []
	
		#our data series
		#twa_ds = pd.Series(dtype='float')
		#tws_ds = pd.Series(dtype='float')
		#bsp_ds = pd.Series(dtype='float')

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

					#only use ones that have the unix time now.
					if 'unix_time' in data:
						#just use the unix timestamp - fast, but we lose timezone info.
						unix_time = float(data['unix_time'])
						pd_time = datetime.datetime.fromtimestamp(unix_time)
					else:
						#convert the human timestamp - needed if you want to edit the data
						pd_time = pd.to_datetime(data['time'])
					
					#lets only parse valid strings
					if not nmea.valid:
						#print(line)
						continue

					#is it a known code?
					if not nmea.known:
						#pprint(output)
						continue

					#wind speed...
					if 'tws' in output and 'twa' in output:
						twa = float(output['twa'])
						tws = float(output['tws'])

						twa_data.append({'time': pd_time, 'data': twa})
						tws_data.append({'time': pd_time, 'data': tws})
							
					#boat speed... use SOG
					if use_sog:
						if 'sog' in output and nmea.sentence == 'RMC' and output['sog']:
							bsp = float(output['sog'])
							bsp_data.append({'time': pd_time, 'data': bsp})
					#or otherwise use BSP
					else:
						if 'water_speed' in output and nmea.sentence == 'VHW' and output['water_speed']:
							bsp = float(output['water_speed'])
							bsp_data.append({'time': pd_time, 'data': bsp})
			else:
				print ("Empty lines...")

		fp.close()	
		
		if not len(twa_data) or not len(tws_data) or not len(bsp_data):
			print("No data in file.")
			continue
			
		#make our dataframes		
		twa_pd = pd.DataFrame.from_records(twa_data, index='time')
		tws_pd = pd.DataFrame.from_records(tws_data, index='time')
		bsp_pd = pd.DataFrame.from_records(bsp_data, index='time')

		#convert it to a series.
		twa_ds = twa_pd.squeeze()
		tws_ds = tws_pd.squeeze()
		bsp_ds = bsp_pd.squeeze()

		#what was our max boat speed?
		max_bsp = bsp_ds.max()

		#do we want a rolling 10s filter?
		if args.filter == 'rolling':
			#how many seconds to filter over?
			seconds = args.filter_seconds

			#do our rolling average
			twa_rolling = twa_ds.rolling('{}s'.format(seconds), center=True).mean()
			tws_rolling = tws_ds.rolling('{}s'.format(seconds), center=True).mean()
			bsp_rolling = bsp_ds.rolling('{}s'.format(seconds), center=True).mean()

			#save the result
			twa_filt = twa_rolling
			tws_filt = tws_rolling
			bsp_filt = bsp_rolling
		#do we want a buttery filter?
		elif args.filter == 'butter':
			#do our butterworth filter
			hz = args.filter_hz
			seconds = math.ceil(1 / hz)
			b = signal.butter(3, hz, analog=False)

			fd = signal.filtfilt(*b, twa_ds.array, padtype='constant')
			twa_butter = pd.Series(data=fd, index=twa_ds.index)
			fd = signal.filtfilt(*b, tws_ds.array, padtype='constant')
			tws_butter = pd.Series(data=fd,index=tws_ds.index)
			fd = signal.filtfilt(*b, bsp_ds.array, padtype='constant')
			bsp_butter = pd.Series(data=fd,index=bsp_ds.index)

			twa_filt = twa_butter
			tws_filt = tws_butter
			bsp_filt = bsp_butter
		#or just the raw data?
		else:
			seconds = 0

			twa_filt = twa_ds
			tws_filt = tws_ds
			bsp_filt = bsp_ds

		#resample to give us regular data every second
		twa_resample = twa_filt.resample('1s').mean()
		tws_resample = tws_filt.resample('1s').mean()
		bsp_resample = bsp_filt.resample('1s').mean()
		
		#the start/end of the data is sketchy from averaging, extrapolation... drop it
		twa_final = twa_resample[seconds:-seconds]
		tws_final = tws_resample[seconds:-seconds]
		bsp_final = bsp_resample[seconds:-seconds]

		#print("Raw Data")
		#print(bsp_ds)
		#print(bsp_ds.describe())
		
		#print("Filtered")
		#print(bsp_filt)
		#print(bsp_filt.describe())

		#print("Resampled")
		#print(bsp_final)
		#print(bsp_final.describe())
		
		#okay, now bin all of our data
		for time, bsp in bsp_final.items():
			twa = twa_final.get(time)
			tws = tws_final.get(time)

			#print("[{}] TWA: {} TWS: {} BSP: {}".format(time, twa, tws, bsp))

			#make sure we got all 3 values and they are valid
			if twa and tws and not math.isnan(twa) and not math.isnan(tws) and not math.isnan(bsp):
				bp.bin_speeds(twa, tws, bsp)

		#
		# Graphs below
		#
				
		scatter_size = 1.0
		line_size = 1.0
		
		#reset our graph.
		#plt.figure()
		fig, (twa_ax, tws_ax, bsp_ax) = plt.subplots(3)
		fig.suptitle("{} ({} Points)".format(os.path.basename(myfile), len(tws_ds.index)))

		#plot our data
		tws_ds.plot(ax=tws_ax, c='#00bf00', label='Raw', marker='.', markersize=scatter_size, linewidth=0, linestyle='None', markeredgewidth=0)
		#tws_rolling.plot(ax=tws_ax, c='orange', label='Rolling', linewidth=line_size)
		#tws_butter.plot(ax=tws_ax, c='purple', label='Filtered', linewidth=line_size)
		tws_final.plot(ax=tws_ax, c='black', label='Resampled', linewidth=line_size)

		#show 0kts as base
		tws_ax.set_ylim([0, None])
		tws_ax.set(ylabel='TWS')
		tws_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
		tws_ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

		#this is to format the x/y info in interactive mode
		def format_tws(x, y):
			formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
			text = formatter.format_data(x)
			return "{} TWS: {:.2f}".format(text, y)
		tws_ax.format_coord = format_tws
		
		#plot our data
		twa_ds.plot(ax=twa_ax, c='#bf0000', label='Raw', marker='.', markersize=scatter_size, linewidth=0, linestyle='None', markeredgewidth=0)
		#twa_rolling.plot(ax=twa_ax, c='orange', label='Rolling', linewidth=line_size)
		#twa_butter.plot(ax=twa_ax, c='purple', label='Filtered', linewidth=line_size)
		twa_final.plot(ax=twa_ax, c='black', label='Resampled', linewidth=line_size)

		#show 0kts as base
		twa_ax.set_ylim([0, None])
		twa_ax.set(ylabel='TWA')
		twa_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
		twa_ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

		#this is to format the x/y info in interactive mode
		def format_twa(x, y):
			formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
			text = formatter.format_data(x)
			return "{} TWA: {}".format(text, round(y))
		twa_ax.format_coord = format_twa

		#plot our data
		bsp_ds.plot(ax=bsp_ax, c='#0000bf', label='Raw', marker='.', markersize=scatter_size, linewidth=0, linestyle='None', markeredgewidth=0)
		#bsp_rolling.plot(ax=bsp_ax, c='orange', label='Rolling', linewidth=line_size)
		#bsp_butter.plot(ax=bsp_ax, c='purple', label='Filtered', linewidth=line_size)
		bsp_final.plot(ax=bsp_ax, c='black', label='Resampled', linewidth=line_size)

		#show 0kts as base
		bsp_ax.set_ylim([0, None])
		bsp_ax.set(ylabel='BSP')
		bsp_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
		bsp_ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

		#this is to format the x/y info in interactive mode
		def format_bsp(x, y):
			formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
			text = formatter.format_data(x)
			return "{} BSP: {:.2f}".format(text, y)
		bsp_ax.format_coord = format_bsp
		
		#auto format our date ticks.
		plt.setp(tws_ax.get_xticklabels(), rotation=0, horizontalalignment='center', fontsize=6)
		plt.setp(twa_ax.get_xticklabels(), rotation=0, horizontalalignment='center', fontsize=6)
		plt.setp(bsp_ax.get_xticklabels(), rotation=0, horizontalalignment='center', fontsize=6)

    	#give us a nicely spaced set of graphs
		fig.tight_layout()    

		#where to save it?
		file_parts = os.path.split(myfile)
		category = os.path.basename(file_parts[0])
		graph_output_dir = "graphs/{}".format(category)

		if not os.path.exists(graph_output_dir):
			os.makedirs(graph_output_dir)
			
		#okay, actually save
		graph_output_file = "{}/data-{}.png".format(graph_output_dir, file_parts[1])
		plt.savefig(graph_output_file, bbox_inches='tight', dpi=600)
		print("Writing data graph to {}. {} points".format(graph_output_file, len(twa_pd)))

		#how many points on this config?
		total_points += len(twa_pd)
    
		#do we want to show the interactive one?
		if args.graph:
			plt.show()

		#finally, clear our graph for the next one
		plt.clf()
		plt.close()

	#cruncho el numero
	if args.graph:
		graph_output_dir = None

	#generate our polars now.
	bp.twa_min = args.twa_min
	bp.twa_max = args.twa_max
	bp.tws_min = args.tws_min
	bp.tws_max = args.tws_max
	all_polars = bp.generate_polars(graph_output_dir, max_bsp)
	
	#lets make a polar chart!
	polar_graph_file = False
	if args.dir:
		polar_graph_file = "graphs/{}/polar-chart.png".format(category)
		title = "{} Polar Chart".format(category.title())
	elif args.file:
		polar_graph_file = "graphs/{}/polar-chart-{}.png".format(category, os.path.basename(args.file))
		title = "{} Polar Chart".format(os.path.basename(args.file))

	all_polars['mean'].polar_chart(args.graph, polar_graph_file, title)
	
	#write our files...
	for idx, polar in all_polars.items():
		fname = "polars/{}-{}.csv".format(polar_name, idx)
		print("Writing results to {}".format(fname))
		polar.write_csv(fname)
		
	print("{} total data points processed.".format(total_points))

if __name__ == '__main__':
	main()
