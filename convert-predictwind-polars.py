#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""convert-predictwind-polars.py
Loads a predictwind polar file and writes it back out in our format.  Will automatically interpolate from variable TWA entries and different TWS columns
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
import boatpolar

import pandas as pd
import numpy as np

def main():
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', action='store', required=True)
	parser.add_argument('-g', '--graph', default=False, action='store_true', help="Show interactive graph. Will always automatically generate .png graph images.")
	
	args = parser.parse_args()
	
	output = boatpolar.BoatPolar()
	tws_data = []

	#did we get a real legend?
	if not os.path.isfile(args.file):
		print ("Predictwind file %s does not exist." % (args.file))
		return False
	else:
		fp = open(args.file)
		reader = csv.reader(fp, dialect='excel-tab')

	polar_df = pd.DataFrame(index=output.wind_angles, columns=output.wind_speeds, dtype='float')

	#loop thru our predict wind file
	for row in reader:
		twa_data = []
		bsp_data = []
		data = row[1:]
		tws = int(row[0])
		
		#each line is TWS with TWA/BSP pairs:
		for i in range(int(len(data)/2)):
			twa = int(data[0+i*2])
			bsp = float(data[1+i*2])
			
			twa_data.append(twa)
			bsp_data.append(bsp)

		#load our dataframe
		pw_df = pd.DataFrame({'bsp': bsp_data}, index=twa_data)
		
		#interpolate each wind speed line
		df_out = pd.DataFrame(index=output.wind_angles)
		df_out.index.name = pw_df.index.name
		for colname, col in pw_df.items():
			df_out[colname] = np.round(np.interp(output.wind_angles, pw_df.index, col), 2)

		#save it to our main dataframe
		polar_df[tws] = df_out['bsp']

	#if the TWS columns dont match up, this will interpolate them.
	interpolated = polar_df.interpolate(axis='columns')

	#finally, save to our polar.
	for tws, df_data in interpolated.items():
		for twa, bsp in df_data.items():
			output.set_speed(twa, tws, bsp)

	#write our combined files
	output.polar_chart(args.graph, "graphs/predictwind-polar.png", "{} Polar".format(args.file))
	output.write_csv("polars/predictwind-converted.csv")
	print("Writing polar to polars/predictwind-converted.csv")
	output.calculate_vmg().write_csv("polars/predictwind-vmg.csv")
	print("Writing vmg to polars/predictwind-vmg.csv")
	
	print("Finished interpolating Predictwind polars")
			
if __name__ == '__main__':
	main()
    
