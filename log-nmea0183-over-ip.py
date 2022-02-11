import socket, time
import pprint
import datetime
import json
import argparse
import os
import nmea0183
from pprint import pprint

def log_data():
    
	#these are our command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--ip', action='store', default='192.168.50.20')
	parser.add_argument('-p', '--port', action='store', default='10110')
	parser.add_argument('-c', '--config', action='store', default='default')
    
	args = parser.parse_args()

	#connect to our socket
	s = socket.socket()
	s.connect((args.ip, int(args.port)))

	#generate our filename
	d = datetime.datetime.today()
	now = d.strftime("%Y-%m-%d %H%M")
	fname = "data/{}/nmea0183-log-{}-{}.txt".format(args.config, args.config, now)

	#does our directory exist?
	if not os.path.exists("data/{}".format(args.config)):
		os.mkdir("data/{}".format(args.config))

	#init our data
	line = ''
	nmea = nmea0183.nmea0183()

	#start our log file
	with open(fname, 'w') as f:
		try:
			#log forever
			while True:
				
				#get data from the receiver
				line += s.recv(1)
				
				#did we get a new line?
				if line[-2:] == '\r\n':
					
					#is it a valid nmea0183 line?
					output = nmea.parseline(line)
					if nmea.valid:
						
						#write our line to our file...
						jdata = {}
						jdata['time'] = datetime.datetime.now().isoformat()
						jdata['unix_time'] = time.time()
						jdata['lines'] = [line[0:-2]]
						f.write(json.dumps(jdata) + "\n")
						
						#is it a known code?
						if output.has_key('sog') and nmea.sentence == 'RMC':
							print('[{}] SOG: {}'.format(nmea.sentence, output['sog']))
						if output.has_key('water_speed') and nmea.sentence == 'VHW':
							print('[{}] BSP: {}'.format(nmea.sentence, output['water_speed']))
						if output.has_key('twa'):
							print('[{}] TWA: {} TWS: {}'.format(nmea.sentence, output['twa'], output['tws']))
					
					#reset our buffer
					line = ''
				
		except Exception as e:
			pprint(e)

	#clean up our socket
	s.close()
		
if __name__ == '__main__':
	log_data()