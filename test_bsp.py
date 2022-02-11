import json
import numpy
import nmea0183
from pprint import pprint

files = ["data/stargazer-spin+1st reef.txt", 'data/stargazer-bowsprit-spin.txt', 'data/stargazer-twin-bow-spin.txt', 'data/stargazer-screacher-and-full-main.txt']
#files = ['data/stargazer-screacher-and-full-main.txt']
#files = ['data/stargazer-bowsprit-spin.txt']
#files = ['data/stargazer-twin-bow-spin.txt']
files = ['data/motorboating/nmea0183-log-motorboating-2022-01-12 1707.txt']

for filename in files:
	fp = open(filename)

	print(filename)
	
	
	
	bsp_arr = {}
	sog_arr = {}
	sogint = 0

	while True:
		json_line = fp.readline()
		if json_line == '':
			break

		try:
			data = json.loads(json_line)
		except ValueError as e:
			continue

		if data['lines'] is not None:
			for line in data['lines']:

				# run it through our parser
				nmea = nmea0183.nmea0183()
				output = nmea.parseline(line)	

				if output.has_key('sog') and nmea.sentence == 'RMC' and output['sog']:
					sog = float(output['sog'])
					sogint = int(sog)
					
					if not sog_arr.has_key(sogint):
						sog_arr[sogint] = []

					sog_arr[sogint].append(sog)

				if output.has_key('water_speed') and nmea.sentence == 'VHW' and output['water_speed']:
					bsp = float(output['water_speed'])

					if not bsp_arr.has_key(sogint):
						bsp_arr[sogint] = []

					bsp_arr[sogint].append(bsp)


	for sogint, sog_data in sog_arr.iteritems():
		bsp_data = bsp_arr[sogint]
		sog = round(numpy.average(sog_data), 2)
		bsp = round(numpy.average(bsp_data), 2)
		ratio = round(sog / bsp, 3)

		#print('SOG len {}'.format(len(sog_data)))
		#print('BSP len {}'.format(len(bsp_data)))
	
		print("Bin {:2d} = {}".format(sogint, ratio))
