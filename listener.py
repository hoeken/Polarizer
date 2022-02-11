import socket, time
import pprint
import datetime
import json
import argparse
import os
import nmea0183
import numpy
from pprint import pprint

def listener():
    
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--ip', action='store', default='192.168.50.20')
	parser.add_argument('-p', '--port', action='store', default='10110')
    
	args = parser.parse_args()

	#connect to our socket
	s = socket.socket()
	s.connect((args.ip, int(args.port)))

	#init our data
	line = ''
	nmea = nmea0183.nmea0183()
	
	old_day = None
	old_hour = None
	old_tenmin = None
	old_minute = None
	
	minute_start_log = None
	minute_start_dtw = None
	minute_sog = []
	minute_bsp = []
	minute_tws = []

	tenmin_start_log = None
	tenmin_start_dtw = None
	tenmin_sog = []
	tenmin_bsp = []
	tenmin_tws = []

	hour_start_log = None
	hour_start_dtw = None
	hour_sog = []
	hour_bsp = []
	hour_tws = []

	day_start_log = None
	day_start_dtw = None
	day_sog = []
	day_bsp = []
	day_tws = []

	log = None
	dtw = None
	sog = None
	bsp = None
	tws = None
	
	#open our log files...
	minute_log = open("data/log-minute.txt", 'a', 0)
	tenmin_log = open("data/log-tenmin.txt", 'a', 0)
	hour_log = open("data/log-hour.txt", 'a', 0)
	day_log = open("data/log-day.txt", 'a', 0)

	#log forever
	while True:
		#get data from the receiver
		line += s.recv(1)
		
		#did we get a new line?
		if line[-2:] == '\r\n':
			#is it a valid nmea0183 line?
			line = line.strip()
			output = nmea.parseline(line)
			if nmea.valid:

				#grab the appropriate data
				try:
					if output.has_key('log_trip') and output['log_trip']:
						log = float(output['log_trip'])
					if output.has_key('distance_to_destination') and output['distance_to_destination']:
						dtw = round(float(output['distance_to_destination']), 1)
					if output.has_key('sog') and nmea.sentence == 'RMC' and output['sog']:
						sog = float(output['sog'])
						minute_sog.append(sog)
						tenmin_sog.append(sog)
						hour_sog.append(sog)
						day_sog.append(sog)
					if output.has_key('water_speed') and nmea.sentence == 'VHW' and output['water_speed']:
						bsp = float(output['water_speed'])
						minute_bsp.append(bsp)
						tenmin_bsp.append(bsp)
						hour_bsp.append(bsp)
						day_bsp.append(bsp)
					if output.has_key('tws') and output['tws']:
						tws = float(output['tws'])
						minute_tws.append(tws)
						tenmin_tws.append(tws)
						hour_tws.append(tws)
						day_tws.append(tws)
				except ValueError as e:
					print("ValueError: {}".line)
					pprint(output)
					
				now = datetime.datetime.now()
				now_day = now.strftime("%Y-%m-%d")
				now_hour = now.strftime("%Y-%m-%d %H")
				now_minute = now.strftime("%Y-%m-%d %H:%M")
				now_tenmin = now_minute[0:-1]
				
				#wait til we get all our data...
				if log != None and dtw != None and sog != None and bsp != None and tws != None:
					
					if now_minute != old_minute:
						if old_minute != None:
							minute_sog = round(numpy.average(minute_sog), 2)
							minute_bsp = round(numpy.average(minute_bsp), 2)
							minute_tws = round(numpy.average(minute_tws), 2)
							minute_sog_bsp_ratio = round(minute_sog / minute_bsp, 2)

							log_str = "MINUTE {} | LOG: {} | DTW: {} | SOG: {} | BSP: {} ({})| TWS: {}".format(now_minute, log, dtw, minute_sog, minute_bsp, minute_sog_bsp_ratio, minute_tws)
							print(log_str)
							
							jdata = {}
							jdata['time'] = now_minute
							jdata['log'] = log
							jdata['dtw'] = dtw
							jdata['sog'] = minute_sog
							jdata['bsp'] = minute_bsp
							jdata['tws'] = minute_tws
													
							minute_log.write(json.dumps(jdata) + "\n")
							minute_log.flush()
					
						old_minute = now_minute
						minute_start_log = log
						minute_start_dtw = dtw
						minute_sog = []
						minute_bsp = []
						minute_tws = []

					if now_tenmin != old_tenmin:
						if old_tenmin != None:
							tenmin_sog = round(numpy.average(tenmin_sog), 2)
							tenmin_bsp = round(numpy.average(tenmin_bsp), 2)
							tenmin_tws = round(numpy.average(tenmin_tws), 2)
							tenmin_sog_bsp_ratio = round(tenmin_sog / tenmin_bsp, 2)

							log_str = "10 MIN {}0 | LOG: {} | DTW: {} | SOG: {} | BSP: {} ({})| TWS: {}".format(now_tenmin, log, dtw, tenmin_sog, tenmin_bsp, tenmin_sog_bsp_ratio, tenmin_tws)
							print(log_str)

							jdata = {}
							jdata['time'] = now_minute
							jdata['log'] = log
							jdata['dtw'] = dtw
							jdata['sog'] = tenmin_sog
							jdata['bsp'] = tenmin_bsp
							jdata['tws'] = tenmin_tws
													
							tenmin_log.write(json.dumps(jdata) + "\n")
							tenmin_log.flush()
					
						old_tenmin = now_tenmin
						tenmin_start_log = log
						tenmin_start_dtw = dtw
						tenmin_sog = []
						tenmin_bsp = []
						tenmin_tws = []

					if now_hour != old_hour:
						if old_hour != None:
							drun = round(log - hour_start_log, 1)
							vmg = round(hour_start_dtw - dtw, 1)
							hour_sog = round(numpy.average(hour_sog), 2)
							hour_bsp = round(numpy.average(hour_bsp), 2)
							hour_tws = round(numpy.average(hour_tws), 2)
							hour_sog_bsp_ratio = round(hour_sog / hour_bsp, 2)

							log_str = "HOUR {}00 | LOG: {} | DRUN: {} | DTW: {} | VMG: {} | SOG: {} | BSP: {} ({})| TWS: {}".format(now_hour, log, drun, dtw, vmg, hour_sog, hour_bsp, hour_sog_bsp_ratio, hour_tws)
							print(log_str)
							
							jdata = {}
							jdata['time'] = now_minute
							jdata['log'] = log
							jdata['drun'] = drun
							jdata['dtw'] = dtw
							jdata['vmg'] = vmg
							jdata['sog'] = hour_sog
							jdata['bsp'] = hour_bsp
							jdata['tws'] = hour_tws
													
							hour_log.write(json.dumps(jdata) + "\n")
							hour_log.flush()
					
						old_hour = now_hour
						hour_start_log = log
						hour_start_dtw = dtw
						hour_sog = []
						hour_bsp = []
						hour_tws = []
					
					if now_day != old_day:
						if old_day != None:
							drun = round(log - day_start_log, 1)
							vmg = round(day_start_dtw - dtw, 1)
							day_sog = round(numpy.average(day_sog), 2)
							day_bsp = round(numpy.average(day_bsp), 2)
							day_tws = round(numpy.average(day_tws), 2)
							day_sog_bsp_ratio = round(day_sog / day_bsp, 2)
							
							log_str = "DAY {} | LOG: {} | DRUN: {} | DTW: {} | VMG: {} | SOG: {} | BSP: {} ({})| TWS: {}".format(now_day, log, drun, dtw, vmg, day_sog, day_bsp, day_sog_bsp_ratio, day_tws)
							print(log_str)

							jdata = {}
							jdata['time'] = now_minute
							jdata['log'] = log
							jdata['drun'] = drun
							jdata['dtw'] = dtw
							jdata['vmg'] = vmg
							jdata['sog'] = day_sog
							jdata['bsp'] = day_bsp
							jdata['tws'] = day_tws
													
							day_log.write(json.dumps(jdata) + "\n")
							day_log.flush()
					
						old_day = now_day
						day_start_log = log
						day_start_dtw = dtw
						day_sog = []
						day_bsp = []
						day_tws = []	
						
				#if output.has_key('sog'):
				#	print("SOG: {}".format(output['sog']))
				#if output.has_key('water_speed'):
				#	print("Water Speed: {}".format(output['water_speed']))

				#if nmea.sentence == 'BWC':
				#	print(nmea.sentence)
				#	print(line)
				#	pprint(output)
					
				#is it a known code?
				#if not nmea.known:
				#	print(line)
				#	pprint(nmea.params)
			#else:
			#	pprint(line)

			#reset our buffer
			line = ''

	#clean up our socket
	s.close()
		
if __name__ == '__main__':
	listener()