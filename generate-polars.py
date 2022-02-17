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
	
		#init our arrays
		twa_list = []
		tws_list = []
		bsp_list = []
		wind_time = 0
		bsp_time = 0

		#this is for graphing... probably a better way to do this.
		tws_data = {}
		tws_avg_data = {}
		twa_data = {}
		twa_avg_data = {}
		bsp_data = {}
		bsp_avg_data = {}

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
					#if 'unix_time' in data:
					#	unix_time = data['unix_time']
					#fucking date times.... old log entries didnt have the unix_time variable
					#else:
					ts = datetime.datetime.strptime(output['time'][0:19], "%Y-%m-%dT%H:%M:%S")
					unix_time = time.mktime(ts.timetuple())
					micros = output['time'][19:]
					if micros != '':
						micros = float(micros)
					else:
						micros = 0.0
					unix_time += micros

					#need this later
					timestamp = datetime.datetime.fromtimestamp(unix_time)

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
						
						tws_data[timestamp] = tws
						twa_data[timestamp] = twa
							
					#boat speed... use SOG
					if use_sog:
						if 'sog' in output and nmea.sentence == 'RMC' and output['sog']:
							bsp = float(output['sog'])
							bsp_list.append(bsp)
							bsp_time = unix_time
							bsp_data[timestamp] = bsp
					else:
						if 'water_speed' in output and nmea.sentence == 'VHW' and output['water_speed']:
							bsp = float(output['water_speed'])
							bsp_list.append(bsp)
							bsp_time = unix_time
							bsp_data[timestamp] = bsp

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
						
						max_bsp = max(max_bsp, avg_bsp)
						
						tws_avg_data[timestamp] = round(avg_tws, 2)
						twa_avg_data[timestamp] = round(avg_twa, 2)
						bsp_avg_data[timestamp] = round(avg_bsp, 2)

						#print("TWA: {} TWS: {} BSP: {}".format(round(avg_twa), round(avg_tws, 2), round(avg_bsp, 2)))

						bp.bin_speeds(avg_twa, avg_tws, avg_bsp)
						#bp.bin_speeds(twa_list[0], tws_list[0], bsp_list[0])
						
						wind_time = 0
						bsp_time = 0
			else:
				print ("Empty lines...")

		fp.close()	
		
		scatter_size = 1
		line_size = 0.3
		
		#reset our graph.
		#plt.figure()
		fig, (twa_ax, tws_ax, bsp_ax) = plt.subplots(3)
		fig.suptitle("{} ({} Points)".format(os.path.basename(myfile), len(tws_data)))

		#this is our TWS portion of the graph
		tws_index = pd.DatetimeIndex(tws_data.keys())
		tws_df = pd.DataFrame({'time': tws_index, 'tws': tws_data}, index=tws_index)
		tws_avg_index = pd.DatetimeIndex(tws_avg_data.keys())
		tws_avg_df = pd.DataFrame({'time': tws_avg_index, 'tws': tws_avg_data}, index=tws_avg_index)

		#raw data as a scatterplot
		x = tws_df['time']
		y = tws_df['tws']
		tws_ax.scatter(x, y, s=scatter_size, c='#00bf00', label='Raw', marker='.', linewidth=0)

		#average as a line plot
		x = tws_avg_df['time']
		y = tws_avg_df['tws']
		tws_ax.plot(x, y, c='black', label='Average', linewidth=line_size)

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
		
		#this is our TWA portion of the graph
		twa_index = pd.DatetimeIndex(twa_data.keys())
		twa_df = pd.DataFrame({'time': twa_index, 'twa': twa_data}, index=twa_index)
		twa_avg_index = pd.DatetimeIndex(twa_avg_data.keys())
		twa_avg_df = pd.DataFrame({'time': twa_avg_index, 'twa': twa_avg_data}, index=twa_avg_index)

		#raw data as a scatterplot
		x = twa_df['time']
		y = twa_df['twa']
		twa_ax.scatter(x, y, s=scatter_size, c='#bf0000', label='Raw', marker='.', linewidth=0)

		#average as a line plot
		x = twa_avg_df['time']
		y = twa_avg_df['twa']
		twa_ax.plot(x, y, c='black', label='Average', linewidth=line_size)

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

		#this is our BSP portion of the graph
		bsp_index = pd.DatetimeIndex(bsp_data.keys())
		bsp_df = pd.DataFrame({'time': bsp_index, 'bsp': bsp_data}, index=bsp_index)
		bsp_avg_index = pd.DatetimeIndex(bsp_avg_data.keys())
		bsp_avg_df = pd.DataFrame({'time': bsp_avg_index, 'bsp': bsp_avg_data}, index=bsp_avg_index)

		#raw data as a scatterplot
		x = bsp_df['time']
		y = bsp_df['bsp']
		bsp_ax.scatter(x, y, s=scatter_size, c='#0000bf', label='Raw', marker='.', linewidth=0)

		#average as a line plot
		x = bsp_avg_df['time']
		y = bsp_avg_df['bsp']
		bsp_ax.plot(x, y, c='black', label='Average', linewidth=line_size)

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
		print("Writing data graph to {}".format(graph_output_file))
    
		#do we want to show the interactive one?
		if args.graph:
			plt.show()

		#finally, clear our graph for the next one
		plt.clf()
		plt.close()


	#cruncho el numero
	if args.graph:
		graph_output_dir = None
	all_polars = bp.generate_polars(graph_output_dir, max_bsp)
	
	#lets make a polar chart!
	polar_graph_file = False
	if args.dir:
		polar_graph_file = "graphs/{}/polar-chart.png".format(category)
	elif args.file:
		polar_graph_file = "graphs/{}/polar-chart-{}.png".format(category, os.path.basename(args.file))

	all_polars['mean'].polar_chart(args.graph, polar_graph_file)
	
	
	#write our files...
	for idx, polar in all_polars.items():
		fname = "polars/{}-{}.csv".format(polar_name, idx)
		print("Writing results to {}".format(fname))
		polar.write_csv(fname)

if __name__ == '__main__':
	main()
    
