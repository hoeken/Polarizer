#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""load-tabular-polars.py
Loads a tabular polar format and do operations on it.
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
	parser.add_argument('-n', '--name', action='store', default="mypolar", help="Name of the output polar")
	parser.add_argument('-g', '--graph', default=False, action='store_true', help="Show interactive graph. Will always automatically generate .png graph images.")
	parser.add_argument('-v', '--vmg', default=False, action='store_true', help="Calculate VMG")
	parser.add_argument('-a', '--apparent', default=False, action='store_true', help="Calculate AWA and AWS")

	args = parser.parse_args()
	
	output = boatpolar.BoatPolar()
	
	#did we get a real legend?
	if not os.path.isfile(args.file):
		print ("Polar file %s does not exist." % (args.file))
		return False
	else:
		polar_df = pd.read_csv(args.file, index_col=0, dtype=float)
		polar_df.index.rename('twa')

	#native TWA list
	twa_list = []
	for twa in polar_df.index:
		twa_list.append(int(twa))
	output.wind_angles = twa_list

	#native TWS list
	tws_list = []
	for tws in polar_df.columns:
		tws_list.append(int(tws))
	output.wind_speeds = tws_list
	
	#this is our interpolation stuff, we might want to save this and re-use someday.
	if False:
		#polar_df = pd.DataFrame(index=output.wind_angles, columns=output.wind_speeds, dtype='float')

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
		polar_df = polar_df.interpolate(axis='columns')

	#finally, save to our polar.
	for tws, df_data in polar_df.items():
		for twa, bsp in df_data.items():
			output.set_speed(twa, tws, bsp)

	#write our combined files
	if args.graph:
		output.polar_chart(args.graph, "graphs/{}-polar.png".format(args.name), "{} Polar".format(args.file))

	output.write_csv("polars/{}-bsp.csv".format(args.name))
	print("Writing polar to polars/{}-bsp.csv".format(args.name))

	if args.vmg:
		output.calculate_vmg().write_csv("polars/{}-vmg.csv".format(args.name))
		print("Writing vmg to polars/{}-vmg.csv".format(args.name))

	if args.apparent:
		best_awa, best_aws = output.calculate_apparent()
		best_awa.write_csv("polars/{}-awa.csv".format(args.name))	
		print("Writing awa to polars/{}-awa.csv".format(args.name))
		best_aws.write_csv("polars/{}-aws.csv".format(args.name))	
		print("Writing aws to polars/{}-aws.csv".format(args.name))
			
	print("Finished processing polars")
			
if __name__ == '__main__':
	main()
    
