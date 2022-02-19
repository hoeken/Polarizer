#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, time
import pprint
import datetime
import json
import argparse
import os
import nmea0183
from pprint import pprint
import pytz

from dateutil import parser
from dateutil import tz

import os, json, uuid

def main():
	utc = tz.tzutc()

	walk_dir = 'data/'
	for root, subdirs, files in os.walk(walk_dir):
		for filename in files:
			file_path = os.path.join(root, filename)

			if filename.endswith('.txt'):
				print('file: %s' % (file_path))

				fp = open(file_path)

				tempfile = os.path.join(os.path.dirname(filename), str(uuid.uuid4()))
				tmp_fp = open(tempfile, 'w')

				while True:
					#read lines until the end of file.
					json_line = fp.readline()
					if json_line == '':
						break;
					
					try:
						data = json.loads(json_line)
					except ValueError as e:
						continue

					#do we even need to look it up?
					if 'timezone' not in data:
						#human_time = parser.parse(data['time'])
						human_time = parser.parse(data['time'])
						human_time = human_time.replace(tzinfo=utc)
						human_unix_time = time.mktime(human_time.timetuple())
	
						#the very earliest ones don't have a unix time!
						if 'unix_time' in data:
							unix_time = datetime.datetime.utcfromtimestamp(data['unix_time'])
							unix_time = unix_time.replace(tzinfo=utc)
							
							#print("Datetime:" + data['time'])
							#print("Timestamp: {}".format(data['unix_time']))
							
							#print("Human: " + human_time.strftime("%Y-%m-%dT%H:%M:%S"))
							#print("UTC: " + unix_time.strftime("%Y-%m-%dT%H:%M:%S"))

							unix_unix_time = time.mktime(unix_time.timetuple())

							#print(human_unix_time)
							#print(unix_unix_time)

							difference = unix_unix_time - human_unix_time
							hours = round(difference / (60*60))
							#print(difference)
							#print(hours)

							timezone = "Etc/GMT-{}".format(hours)
							#print(timezone)

							local_tz = tz.gettz(timezone)
							local_time = datetime.datetime.utcfromtimestamp(data['unix_time'])
							local_time = unix_time.astimezone(local_tz)
						#its wrong, but just default it to UTC
						else:
							timezone = 'UTC'
							data['unix_time'] = human_unix_time

						#local_tz = pytz.timezone(timezone)
						#print("Local: " + local_time.strftime("%Y-%m-%dT%H:%M:%S"))
						#print(local_time.tzinfo)
						
						data['timezone'] = timezone
						
					#write it back!
					tmp_fp.write(json.dumps(data) + "\n")

				fp.close()
				tmp_fp.close()

				os.replace(tempfile, file_path)

if __name__ == '__main__':
	main()
