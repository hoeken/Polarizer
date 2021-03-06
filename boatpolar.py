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
import os

import numpy as np
import matplotlib.pyplot as plt

class BoatPolar:

	#hoeken's standard...
	wind_angles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
	wind_speeds = [0, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 25, 30, 35, 40]

	#min/max values
	twa_min = 0
	twa_max = 180
	tws_min = 0
	tws_max = 40

	awa_min = 0
	awa_max = 180
	aws_min = 0
	aws_max = 40

	#VPP from DuToit...
	#wind_angles = [40, 45, 52, 60, 70, 80, 90, 100, 110, 120, 135, 150, 160, 170, 180]
	#wind_speeds = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 25]

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
		
		try:
			if math.isnan(bsp):
				bsp = 0
		except Exception as e:
			True

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

	def calculate_vmg(self):
		vmg_polar = BoatPolar()
		for tws in self.wind_speeds:
			for twa in self.wind_angles:
				bsp = self.get_speed(twa, tws)
				
				if bsp:
					#calculate our up/downwind vmg
					if twa > 90:
						vmg = math.cos(math.radians(180 - twa)) * bsp
					else:
						vmg = math.cos(math.radians(twa)) * bsp
					vmg = round(vmg, 2)

					vmg_polar.set_speed(twa, tws, vmg)
		
		return vmg_polar

	def calculate_single_apparent(self, twa, tws, bsp):
		bsp_x = 0
		bsp_y = bsp
		true_x = tws * math.sin(math.radians(twa))
		true_y = tws * math.cos(math.radians(twa))

		app_x = bsp_x + true_x
		app_y = bsp_y + true_y
		
		if twa == 0:
			awa = 0
		elif twa == 180:
			awa = 180
		else:
			awa = 90 - math.degrees(math.atan(app_y / app_x))

		aws = math.sqrt(app_x ** 2 + app_y ** 2)
		
		awa = round(awa, 1)
		aws = round(aws, 1)
		
		return awa, aws


	def calculate_apparent(self):
		awa_polar = BoatPolar()
		aws_polar = BoatPolar()

		for tws in self.wind_speeds:
			for twa in self.wind_angles:
				bsp = self.get_speed(twa, tws)
				
				if bsp:
					awa, aws = self.calculate_single_apparent(twa, tws, bsp)
					#print("TWA: {} TWS: {} BSP: {} AWA: {} AWS: {}".format(twa, tws, bsp, awa, aws))

					awa_polar.set_speed(twa, tws, awa)
					aws_polar.set_speed(twa, tws, aws)
		
		return awa_polar, aws_polar


	def generate_polars(self, graph_dir=None, max_bsp=15):
		
		polars = {}
		polars['mean'] = BoatPolar()
		polars['count'] = BoatPolar()
		polars['stddev'] = BoatPolar()
		
		#loop through twa/tws
		for speed in self.wind_speeds:
			for angle in self.wind_angles:
					#get our datapoints
					mybin = self.bins[speed][angle]

					#do we have enough?
					if len(mybin) >= 50:

						#filter here on twa/tws
						if speed < self.tws_min or speed > self.tws_max:
							print("TWS LIMIT - TWA: {} TWS: {}".format(angle, speed))
							continue
						elif angle < self.twa_min or angle > self.twa_max:
							print("TWA LIMIT - TWA: {} TWS: {}".format(angle, speed))
							continue

						#calculationes
						bin_mean = round(numpy.average(self.bins[speed][angle]), 2)
						bin_count = len(mybin)
						bin_median = round(numpy.median(self.bins[speed][angle]), 2)
						bin_stddev = round(numpy.std(self.bins[speed][angle]), 3)

						#run our average on +/- 1 standard deviation
						filtered = []
						for sog in self.bins[speed][angle]:
							if sog >= bin_median - bin_stddev and sog <= bin_median + bin_stddev:
								filtered.append(sog)
						filtered_count = len(filtered)
						bin_mean = round(numpy.average(filtered), 2)

						#filter here on awa/aws
						awa, aws = self.calculate_single_apparent(angle, speed, bin_mean)
						if aws < self.aws_min or aws > self.aws_max:
							print("AWS LIMIT - TWA: {} TWS: {} BSP: {} AWA: {} AWS: {}".format(angle, speed, bin_mean, awa, aws))
							continue
						elif awa < self.awa_min or awa > self.awa_max:
							print("AWA LIMIT - TWA: {} TWS: {} BSP: {} AWA: {} AWS: {}".format(angle, speed, bin_mean, awa, aws))
							continue

						#record our results
						polars['mean'].set_speed(angle, speed, bin_mean)
						polars['count'].set_speed(angle, speed, bin_count)
						polars['stddev'].set_speed(angle, speed, bin_stddev)
						
						#
						# Only Graph After Here
						#

						#std dev lines
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

		#figure out our vmg
		polars['vmg'] = polars['mean'].calculate_vmg()

		#apparent too		
		awa_polar, aws_polar = polars['mean'].calculate_apparent()
		polars['awa'] = awa_polar
		polars['aws'] = aws_polar

		return polars

	def write_csv(self, filename, polars = None):

		#we need our container folder
		mydir = os.path.dirname(filename)
		if not os.path.exists(mydir):
			os.makedirs(mydir)

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

		#we need our container folder
		mydir = os.path.dirname(filename)
		if not os.path.exists(mydir):
			os.makedirs(mydir)

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
				
	def polar_chart(self, show_graph = False, output_filename = False, title = None):
	
		#we need our container folder
		mydir = os.path.dirname(output_filename)
		if not os.path.exists(mydir):
			os.makedirs(mydir)

		#set it up to be a half polar
		fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

		ax.set_thetamin(0)
		ax.set_thetamax(180)
		ax.set_theta_zero_location("N")  # theta=0 at the top
		ax.set_theta_direction(-1)  # theta increasing clockwise

		#set our angle ticks
		ticks = []
		for t in range(0, 181, 15):
		#for t in self.wind_angles:
			ticks.append(math.radians(t))
		ax.set_xticks(ticks)

		#what title?
		if title is not None:
			ax.set_title(title)
		else:
			ax.set_title("Polar Speed Diagram")

		for tws in self.wind_speeds:
			r = []
			theta = []

			for twa in self.wind_angles:
				bsp = self.get_speed(twa, tws)

				if bsp:

					theta.append(math.radians(twa))
					r.append(bsp)

			if len(r):
				ax.plot(theta, r, label="{} kts".format(tws), linewidth=1.0)
		

		#give us a nicely spaced set of graphs
		fig.tight_layout()    

		angle = np.deg2rad(180)
		#ax.legend(loc="lower left", bbox_to_anchor=(-.7 + np.cos(angle)/2, .5 + np.sin(angle)/2))
		plt.legend(title="True Wind Speed", loc='center right', bbox_to_anchor=(.7 + np.cos(angle)/2, .5 + np.sin(angle)/2))

		#okay, actually save
		if output_filename:
			plt.savefig(output_filename, bbox_inches='tight', dpi=600)
			print("Writing polar chart to {}".format(output_filename))

		#do we want to show it?
		if show_graph:
			plt.show()
		
		plt.clf()
		plt.close()

