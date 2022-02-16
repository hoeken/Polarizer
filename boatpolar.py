#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""BoatPolar
A class for working with sailing polars.
"""

__author__ = "Zach Hoeken"
__copyright__ = "Copyright 2022, Zach Hoeken"
__credits__ = ["Zach Hoeken"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Zach Hoeken"
__email__ = "hoeken@gmail.com"
__status__ = "Beta"

import datetime
import time
import numpy
import csv
import math
from pprint import pprint

import numpy as np
import matplotlib.pyplot as plt

class BoatPolar:

	#tws = None
	#twa = None
	#wind_time = 0
	
	#sog = None
	#speed_time = 0
	
	#hoeken's standard...
	#wind_angles = [40, 45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
	#wind_speeds = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

	#VPP from DuToit...
	wind_angles = [40, 45, 52, 60, 70, 80, 90, 100, 110, 120, 135, 150, 160, 170, 180]
	wind_speeds = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 25]

	def __init__(self):
		self.bins = {}
		for speed in self.wind_speeds:
			angle_bin = {}
			for angle in self.wind_angles:
				angle_bin[angle] = []
			self.bins[speed] = angle_bin

		self.polar = {}
		for speed in self.wind_speeds:
			angle_bin = {}
			for angle in self.wind_angles:
				angle_bin[angle] = None
			self.polar[speed] = angle_bin
	
	def set_speed(self, twa, tws, bsp):
		twa = int(twa)
		tws = int(tws)

		self.polar[tws][twa] = bsp

	def get_speed(self, twa, tws):
		tws = int(tws)
		twa = int(twa)
		
		return self.polar[tws][twa]
	
	def bin_speeds(self, twa, tws, bsp):
		
		#only real values
		if tws is None or twa is None or bsp is None:
			return
		else:
			tws = float(tws)
			twa = float(twa)
			bsp = float(bsp)
		
			speed_bin = 0
			best_delta = 1000
			for speed in self.wind_speeds:
				delta = abs(speed - tws)
				if (delta < best_delta):
					best_delta = delta
					speed_bin = speed

			angle_bin = 0
			best_delta = 1000
			for angle in self.wind_angles:
				delta = abs(angle - twa)
				if (delta < best_delta):
					best_delta = delta
					angle_bin = angle

			self.bins[speed_bin][angle_bin].append(bsp)

	def load_polar(self, fp):

		csv_reader = csv.reader(fp)
		i = 0
		for row in csv_reader:
			if i == 0:
				header = row[1:]
			else:
				twa = int(row[0])
				speeds = row[1:]

				for j in range(len(speeds)):
					tws = int(header[j])

					boat_speed = speeds[j]
					if boat_speed != '':
						boat_speed = float(boat_speed)
					else:
						boat_speed = 0.0
						
					self.set_speed(twa, tws, boat_speed)
			i += 1

	def generate_polars(self, graph_dir=None, max_bsp=15):
		
		polars = {}
		polars['mean'] = BoatPolar()
		polars['median'] = BoatPolar()
		polars['diff'] = BoatPolar()
		polars['count'] = BoatPolar()
		polars['stddev'] = BoatPolar()
		polars['vmg'] = BoatPolar()
		
		for speed in self.wind_speeds:
			for angle in self.wind_angles:

				mybin = self.bins[speed][angle]
				if len(mybin) >= 50:

					bin_stddev = round(numpy.std(self.bins[speed][angle]), 3)
					bin_median = round(numpy.median(self.bins[speed][angle]), 2)
					bin_count = len(mybin)
					bin_mean = round(numpy.average(self.bins[speed][angle]), 2)
					bin_diff = round(bin_median - bin_mean, 2)
					
					#this is an attempt to filter out major outliers
					filtered = []
					for sog in self.bins[speed][angle]:
						if sog >= bin_median - bin_stddev and sog <= bin_median + bin_stddev:
							filtered.append(sog)
					bin_filtered = round(numpy.average(filtered), 2)
					bin_mean = bin_filtered
					filtered_count = len(filtered)

					#calculate our up/downwind vmg
					if angle > 90:
						bin_vmg = math.cos(math.radians(180 - angle)) * bin_mean
					else:
						bin_vmg = math.cos(math.radians(angle)) * bin_mean
					bin_vmg = round(bin_vmg, 2)

					#record our results
					polars['mean'].set_speed(angle, speed, bin_mean)
					polars['median'].set_speed(angle, speed, bin_median)
					polars['diff'].set_speed(angle, speed, bin_diff)
					polars['count'].set_speed(angle, speed, bin_count)
					polars['stddev'].set_speed(angle, speed, bin_stddev)
					polars['vmg'].set_speed(angle, speed, bin_vmg)
					
					#where do we graph it to?
					#some lines
					plt.axvline(x=bin_mean, c='red', label="BSP ({})".format(bin_mean), linewidth=0.5, zorder=3, alpha = 0.5)
					plt.axvspan(bin_mean-bin_stddev, bin_mean+bin_stddev, color='red', linewidth=0, alpha=0.1, zorder=3, label = '+/- 1 Sigma')

					#plot the histogram
					x = self.bins[speed][angle]
					plt.hist(x, bins=50, zorder=2)

					#set our titles and axes.
					title = '{}kts TWS @ {} TWA ({} Total Points)'.format(speed, angle, len(mybin))
					plt.gca().set(title=title, ylabel='Count');
					ax = plt.gca()
					ax.set_xlim([0, 15])
					plt.legend()

					#should we show interactive?
					#plt.show()

					#okay, actually save
					if graph_dir:
						graph_output_file = "{}/histogram-{}TWS-{}TWA.png".format(graph_dir, speed, angle)
						plt.savefig(graph_output_file, bbox_inches='tight', dpi =600)

					plt.clf()
					plt.close()
					
		return polars

	def write_csv(self, filename, polars = None):

		if polars is None:
			polars = self.polar
			
		with open(filename, 'w') as f:
			
			csv_writer = csv.writer(f)
			
			header = ['']
			for speed in self.wind_speeds:
				header.append(speed)
			csv_writer.writerow(header)

			for angle in self.wind_angles:
				row = [angle]
				for speed in self.wind_speeds:
					row.append(polars[speed][angle])
				csv_writer.writerow(row)
		
	def write_predictwind(self, filename):	

		with open(filename, 'w') as f:
			
			csv_writer = csv.writer(f, dialect='excel-tab')
			
			for tws in self.wind_speeds:
				row = [tws]
				for twa in self.wind_angles:
					row.append(twa)
					bsp = self.get_speed(twa, tws)
					if bsp is not None:
						row.append(bsp)
					else:
						row.append(0.0)
				csv_writer.writerow(row)
				
	def polar_chart(self):
	
		#wind_angles = [40, 45, 52, 60, 70, 80, 90, 100, 110, 120, 135, 150, 160, 170, 180]
		#wind_speeds = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 25]

		#set it up to be a half polar
		fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

		ax.set_thetamin(0)
		ax.set_thetamax(180)
		ax.set_theta_zero_location("N")  # theta=0 at the top
		ax.set_theta_direction(-1)  # theta increasing clockwise

		#ax.set_rticks([0.5, 1, 1.5, 2])  # Less radial ticks
		#ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
		#ax.grid(True)
		ax.set_title("Polar Speed Diagram", va='bottom')

		for tws in self.wind_speeds:
			r = []
			theta = []

			for twa in self.wind_angles:
				bsp = self.get_speed(twa, tws)

				if bsp:

					theta.append(math.radians(twa))
					r.append(bsp)

			if len(r):
				ax.plot(theta, r, label="TWS: {}".format(tws))
		

		#give us a nicely spaced set of graphs
		fig.tight_layout()    

		angle = np.deg2rad(180)
		#ax.legend(loc="lower left", bbox_to_anchor=(-.7 + np.cos(angle)/2, .5 + np.sin(angle)/2))
		plt.legend(loc='center right', bbox_to_anchor=(.7 + np.cos(angle)/2, .5 + np.sin(angle)/2))
		plt.show()
		
		plt.clf()
		plt.close()

