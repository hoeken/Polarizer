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

def generate_polars():
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', action='store')
	parser.add_argument('-d', '--dir', action='store')
	parser.add_argument('-p', '--polar', action='store')
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
					if data.has_key('unix_time'):
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
					if output.has_key('tws') and output.has_key('twa'):
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
							
					#boat speed... use SOG
					if use_sog:
						if output.has_key('sog') and nmea.sentence == 'RMC' and output['sog']:
							bsp = float(output['sog'])
							bsp_list.append(bsp)
							bsp_time = unix_time
					else:
						if output.has_key('water_speed') and nmea.sentence == 'VHW' and output['water_speed']:
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
	for idx, polar in all_polars.iteritems():
		fname = "polars/{}-{}.csv".format(polar_name, idx)
		print("Writing results to {}".format(fname))
		polar.write_csv(fname)
		
if __name__ == '__main__':
	generate_polars()
    
