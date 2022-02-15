#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""nmea0183
Parser for NMEA0183, a ridiculously archaic data format that is almost 40 years old and yet still in use.  Ya love to see it.
"""

__author__ = "Zach Hoeken"
__copyright__ = "Copyright 2022, Zach Hoeken"
__credits__ = ["Zach Hoeken"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Zach Hoeken"
__email__ = "hoeken@gmail.com"
__status__ = "Beta"

from pprint import pprint
import datetime
import math

class nmea0183:
	
	def __init__(self):
		return
	
	def parseline(self, line):
		
		#clean up any whitespace
		line = line.strip()
		
		#basic init
		self.code = None
		self.talker = None
		self.sentence = None
		self.params = {}
		self.known = True
		output = {}

		#make sure it is a valid sentence first
		self.valid = False
		if self.verifyline(line):
			self.valid = True

			#pull out our message identifiers
			params = line[1:-3].split(',')
			self.code = params[0]
			self.talker = self.code[0:2]
			self.sentence = self.code[2:]
			self.params = params
			output = {}

			try:
				#AAM Waypoint Arrival Alarm
				if self.sentence == 'AAM':
					output = self.parse_AAM(params)
				#APB Autopilot Sentence "B"
				elif self.sentence == 'APB':
					output = self.parse_APB(params)
				#ALM GPS Almanac Data
				elif self.sentence == 'ALM':
					output = self.parse_ALM(params)
				#APA Autopilot Sentence "A"
				elif self.sentence == 'APA':
					output = self.parse_APA(params)
				#APB Autopilot Sentence "B"
				elif self.sentence == 'APB':
					output = self.parse_APB(params)
				#BEC Bearing & Distance to Waypoint - Dead Reckoning
				elif self.sentence == 'BEC':
					output = self.parse_BEC(params)
				#BOD Bearing - Waypoint to Waypoint
				elif self.sentence == 'BOD':
					output = self.parse_BOD(params)
				#BWC Bearing and Distance to Waypoint - Latitude, N/S, Longitude, E/W, UTC, Status
				elif self.sentence == 'BWC':
					output = self.parse_BWC(params)
				#BWR Bearing and Distance to Waypoint - Rhumb Line Latitude, N/S, Longitude, E/W, UTC, Status
				elif self.sentence == 'BWR':
					output = self.parse_BWR(params)
				#BWW Bearing - Waypoint to Waypoint
				elif self.sentence == 'BWW':
					output = self.parse_BWW(params)
				#DBK Depth Below Keel
				elif self.sentence == 'DBK':
					output = self.parse_DBK(params)
				#DBS Depth Below Surface
				elif self.sentence == 'DBS':
					output = self.parse_DBS(params)
				#DBT Depth Below Transducer
				elif self.sentence == 'DBT':
					output = self.parse_DBT(params)
				#DPT Heading - Deviation & Variation
				elif self.sentence == 'DPT':
					output = self.parse_DPT(params)
				#FSI Frequency Set Information
				elif self.sentence == 'FSI':
					output = self.parse_FSI(params)
				#GGA Global Positioning System Fix Data. Time, Position and fix related data for a GPS receiver
				elif self.sentence == 'GGA':
					output = self.parse_GGA(params)
				#GLC Geographic Position, Loran-C
				elif self.sentence == 'GLC':
					output = self.parse_GLC(params)				
				#GLL Geographic Position - Latitude/Longitude
				elif self.sentence == 'GLL':
					output = self.parse_GLL(params)
				#GSA GPS DOP and active satellites
				elif self.sentence == 'GSA':
					output = self.parse_GSA(params)
				#GSV Satellites in view
				elif self.sentence == 'GSV':
					output = self.parse_GSV(params)
				#GTD Geographic Location in Time Differences
				elif self.sentence == 'GTD':
					output = self.parse_GTD(params)
				#HDG Heading - Deviation & Variation
				elif self.sentence == 'HDG':
					output = self.parse_HDG(params)
				#HDM Heading - Magnetic
				elif self.sentence == 'HDM':
					output = self.parse_HDM(params)
				#HDT Heading - True
				elif self.sentence == 'HDT':
					output = self.parse_HDT(params)
				#HSC Heading Steering Command
				elif self.sentence == 'HSC':
					output = self.parse_HSC(params)
				#LCD Loran-C Signal Data
				elif self.sentence == 'LCD':
					output = self.parse_LCD(params)
				#MSK MSK Receiver Interface (for DGPS Beacon Receivers)
				elif self.sentence == 'MSK':
					output = self.parse_MSK(params)
				#MTW Water Temperature
				elif self.sentence == 'MTW':
					output = self.parse_MTW(params)
				#MWV Wind Speed and Angle
				elif self.sentence == 'MWV':
					output = self.parse_MWV(params)
				#MWD Wind Direction & Speed
				elif self.sentence == 'MWD':
					output = self.parse_MWD(params)	
				#OSD Own Ship Data
				elif self.sentence == 'OSD':
					output = self.parse_OSD(params)
				#ROO Waypoints in Active Route
				elif self.sentence == 'ROO':
					output = self.parse_ROO(params)
				#RMA Recommended Minimum Navigation Information
				elif self.sentence == 'RMA':
					output = self.parse_RMA(params)
				#RMB Recommended Minimum Navigation Information
				elif self.sentence == 'RMB':
					output = self.parse_RMB(params)
				#RMC Recommended Minimum Navigation Information
				elif self.sentence == 'RMC':
					output = self.parse_RMC(params)
				#ROT Rate Of Turn
				elif self.sentence == 'ROT':
					output = self.parse_ROT(params)
				#RPM Revolutions
				elif self.sentence == 'RPM':
					output = self.parse_RPM(params)
				#RSA Rudder Sensor Angle
				elif self.sentence == 'RSA':
					output = self.parse_RSA(params)
				#RSD RADAR System Data
				elif self.sentence == 'RSD':
					output = self.parse_RSD(params)
				#RTE Routes
				elif self.sentence == 'RTE':
					output = self.parse_RTE(params)
				#SFI Scanning Frequency Information
				elif self.sentence == 'SFI':
					output = self.parse_SFI(params)
				#STN Multiple Data ID
				elif self.sentence == 'STN':
					output = self.parse_STN(params)
				#TLL Target Latitude and Longitude
				elif self.sentence == 'TLL':
					output = self.parse_TLL(params)
				#TTM Tracked Target Message
				elif self.sentence == 'TTM':
					output = self.parse_TTM(params)
				#VBW Dual Ground/Water Speed
				elif self.sentence == 'VBW':
					output = self.parse_VBW(params)
				#VDR Set and Drift
				elif self.sentence == 'VDR':
					output = self.parse_VDR(params)
				#VHW Water Speed and Heading
				elif self.sentence == 'VHW':
					output = self.parse_VHW(params)
				#VLW Distance Traveled through Water
				elif self.sentence == 'VLW':
					output = self.parse_VLW(params)
				#VPW Speed - Measured Parallel to Wind
				elif self.sentence == 'VPW':
					output = self.parse_VPW(params)
				#VTG Track Made Good and Ground Speed
				elif self.sentence == 'VTG':
					output = self.parse_VTG(params)
				#VWR Relative Wind Speed and Angle
				elif self.sentence == 'VWR':
					output = self.parse_VWR(params)
				#WCV Waypoint Closure Velocity
				elif self.sentence == 'WCV':
					output = self.parse_WCV(params)
				#WNC Distance - Waypoint to Waypoint
				elif self.sentence == 'WNC':
					output = self.parse_WNC(params)
				#WPL Waypoint Location
				elif self.sentence == 'WPL':
					output = self.parse_WPL(params)
				#XDR Cross Track Error - Dead Reckoning
				elif self.sentence == 'XDR':
					output = self.parse_XDR(params)
				#XTE Cross-Track Error - Measured
				elif self.sentence == 'XTE':
					output = self.parse_XTE(params)
				#XTR Cross Track Error - Dead Reckoning
				elif self.sentence == 'XTR':
					output = self.parse_XTR(params)
				#ZDA Time & Date - UTC, Day, Month, Year and Local Time Zone
				elif self.sentence == 'ZDA':
					output = self.parse_ZDA(params)
				#ZFO UTC & Time from Origin Waypoint
				elif self.sentence == 'ZFO':
					output = self.parse_ZFO(params)
				#ZTG UTC & Time to Destination Waypoint
				elif self.sentence == 'ZTG':
					output = self.parse_ZTG(params)
				else:
					self.known = False
			except AttributeError as e:
				#print ("Unknown code {}".format(self.code))
				#pprint(params)
				self.known = False
				output = {}

		return output
	
	#AAM Waypoint Arrival Alarm
	def parse_AAM(self, params, output = {}):
		if params[1] == 'A':
			output['circle_entered'] = True
		else:
			output['circle_entered'] = False

		if params[2] == 'A':
			output['waypoint_perpendicular'] = True
		else:
			output['waypoint_perpendicular'] = False

		output['circle_radius'] = params[3]
		output['waypoint_id'] = params[5]
		
		return output
	
	#ALM GPS Almanac Data
	def parse_ALM(self, params, output = {}):
		output['messages'] = params[1]
		output['message_id'] = params[2]
		output['satellite_prn_number'] = params[3]
		output['gps_week_number'] = params[4]
		output['sv_health'] = params[5]
		output['eccentricity'] = params[6]
		output['almanac_reference_time'] = params[7]
		output['inclination_angle'] = params[8]
		output['rate_of_right_ascension'] = params[9]
		output['root_of_semi_major_axis'] = params[10]
		output['argument_of_perigee'] = params[11]
		output['longitude_of_ascension_node'] = params[12]
		output['mean_anomaly'] = params[13]
		output['f0_clock_parameter'] = params[14]
		output['f1_clock_parameter'] = params[15]

		return output		
	
	#APA Autopilot Sentence "A"
	def parse_APA(self, params, output = {}):
		output['xte'] = float(params[3])
		if params[4] == 'L':
			output['xte'] = -output['xte']
		
		if params[6] == 'A':
			output['circle_entered'] = True
		else:
			output['circle_entered'] = False

		if params[7] == 'A':
			output['waypoint_perpendicular'] = True
		else:
			output['waypoint_perpendicular'] = False
		
		if params[9] == 'T':
			output['destination_bearing_true'] = params[8]
		else:
			output['destination_bearing_magnetic'] = params[8]
			
		output['waypoint_id'] = params[10]
		
		return output
			
	#APB Autopilot Sentence "B"
	def parse_APB(self, params, output = {}):
		output['xte'] = float(params[3])
		if params[4] == 'L':
			output['xte'] = -output['xte']
		
		if params[6] == 'A':
			output['circle_entered'] = True
		else:
			output['circle_entered'] = False

		if params[7] == 'A':
			output['waypoint_perpendicular'] = True
		else:
			output['waypoint_perpendicular'] = False
		
		if params[9] == 'T':
			output['destination_bearing_true'] = params[8]
		else:
			output['destination_bearing_magnetic'] = params[8]
			
		if params[12] == 'T':
			output['bearing_to_waypoint_true'] = params[11]
		else:
			output['bearing_to_waypoint_magnetic'] = params[11]
			
		if params[14] == 'T': 
			output['heading_to_steer_true'] = params[13]
		else:
			output['heading_to_steer_magnetic'] = params[13]

		output['waypoint_id'] = params[10]
		
		return output

	#BEC Bearing & Distance to Waypoint - Dead Reckoning
	def parse_BEC(self, params, output = {}):
		output['utc_time'] = params[1]
		output['waypoint_latitude'] = self.parse_latitude(params[2], params[3])
		output['waypoint_longitude'] = self.parse_longitude(params[4], params[5])
		output['bearing_to_waypoint_true'] = params[6]
		output['bearing_to_waypoint_magnetic'] = params[8]
		output['distance_to_waypoint'] = params[10]
		output['waypoint_id'] = params[12]
		
		return output
	
	
	#BOD Bearing - Waypoint to Waypoint
	def parse_BOD(self, params, output = {}):
		output['bearing_to_waypoint_true'] = params[1]
		output['bearing_to_waypoint_magnetic'] = params[3]
		output['to_waypoint_id'] = params[5]
		output['from_waypoint_id'] = params[6]
		
		return output

	#BWC Bearing and Distance to Waypoint - Latitude, N/S, Longitude, E/W, UTC, Status
	def parse_BWC(self, params, output = {}):
		output['utc_time'] = params[1]
		output['waypoint_latitude'] = self.parse_latitude(params[2], params[3])
		output['waypoint_longitude'] = self.parse_longitude(params[4], params[5])
		output['bearing_to_waypoint_true'] = params[6]
		output['bearing_to_waypoint_magnetic'] = params[8]
		output['distance_to_destination'] = params[10]
		output['to_waypoint_id'] = params[12]
		
		return output
	
	#BWR Bearing and Distance to Waypoint - Rhumb Line Latitude, N/S, Longitude, E/W, UTC, Status
	def parse_BWR(self, params, output = {}):
		output['utc_time'] = params[1]
		output['waypoint_latitude'] = self.parse_latitude(params[2], params[3])
		output['waypoint_longitude'] = self.parse_longitude(params[4], params[5])
		output['bearing_to_waypoint_true'] = params[6]
		output['bearing_to_waypoint_magnetic'] = params[8]
		output['distance_to_destination'] = params[10]
		output['to_waypoint_id'] = params[12]
		
		return output
	
	#BWW Bearing - Waypoint to Waypoint
	def parse_BWW(self, params, output = {}):
		output['bearing_degrees_true'] = params[1]
		output['bearing_degrees_magnetic'] = params[3]
		output['to_waypoint_id'] = params[5]
		output['from_waypoint_id'] = params[6]

		return output
	
	#DBK Depth Below Keel
	def parse_DBK(self, params, output = {}):
		output['keel_depth_feet'] = params[1]
		output['keel_depth_meters'] = params[3]
		output['keel_depth_fathoms'] = params[5]

		return output

	#DBS Depth Below Surface
	def parse_DBS(self, params, output = {}):
		output['surface_depth_feet'] = params[1]
		output['surface_depth_meters'] = params[3]
		output['surface_depth_fathoms'] = params[5]

		return output
	
	#DBT Depth Below Transducer
	def parse_DBT(self, params, output = {}):
		if params[1] != '':
			output['transducer_depth_feet'] = params[1]
			output['transducer_depth_meters'] = params[3]
			output['transducer_depth_fathoms'] = params[5]
		else:
			self.valid = False

		return output
	
	#DPT Depth Transducer
	def parse_DPT(self, params, output = {}):
		output['transducer_depth_meters'] = params[1]
		output['transducer_offset'] = params[2]

		return output
	
	#FSI Frequency Set Information
	def parse_FSI(self, params, output = {}):
		output['transmitting_frequency'] = params[1]
		output['receiving_frequency'] = params[2]
		output['communications_mode'] = params[3]
		output['power_level'] = params[4]

		return output
	
	#GGA Global Positioning System Fix Data. Time, Position and fix related data
	def parse_GGA(self, params, output = {}):
		output['utc_time'] = params[1]
		output['latitude'] = self.parse_latitude(params[2], params[3])
		output['longitude'] = self.parse_longitude(params[4], params[5])
		output['gps_quality'] = params[6]
		output['gps_satellites'] = params[7]
		output['hdop'] = params[8]
		output['altitude'] = params[9]

		return output

	#GLC Geographic Position, Loran-C
	def parse_GLC(self, params, output = {}):
		output['gri_microseconds'] = params[1]

		return output

	#GLL Geographic Position - Latitude/Longitude
	def parse_GLL(self, params, output = {}):
		if params[6] == 'A':
			output['latitude'] = self.parse_latitude(params[1], params[2])
			output['longitude'] = self.parse_longitude(params[3], params[4])
			output['utc_time'] = params[5]
		else:
			self.valid = False

		return output
	
	#GSA GPS DOP and active satellites
	def parse_GSA(self, params, output = {}):
		output['selection_mode'] = params[1]
		output['mode'] = params[2]
		output['satellites'] = []
		for i in range(12):
			if params[3+i] != '':
				output['satellites'].append(params[3+i])
		output['pdop'] = params[15]
		output['hdop'] = params[16]
		output['vdop'] = params[17]

		return output
	
	#GSV Satellites in view
	def parse_GSV(self, params, output = {}):
		output['messages'] = params[1]
		output['message_id'] = params[2]
		output['satellites_in_view'] = params[3]
		
		output['satellites'] = []
		total = int(math.floor((len(params) - 4) / 4))
		for i in range(total):
			sat = {}
			sat['number'] = params[4+i*4]
			sat['elevation'] = params[5+i*4]
			sat['azimuth'] = params[6+i*4]
			sat['snr'] = params[7+i*4]
			output['satellites'].append(sat)

		return output	
	
	#GTD Geographic Location in Time Differences
	def parse_GTD(self, params, output = {}):
		output['time_difference'] = []
		for i in range(5):
			output['time_difference'].append(params[i])
		
		return output

	#HDG Heading - Deviation & Variation
	def parse_HDG(self, params, output = {}):
		output['heading_magnetic'] = params[1]

		if params[2]:
			output['heading_deviation'] = float(params[2])
			if params[3] == 'W':
				output['heading_deviation'] = -output['heading_deviation']
		else:
			output['heading_deviation'] = 0

		if params[4]:
			output['heading_variation'] = float(params[4])
			if params[5] == 'W':
				output['heading_variation'] = -output['heading_variation']
		else:
			output['heading_variation'] = 0

		return output

	#HDM Heading - Magnetic
	def parse_HDM(self, params, output = {}):
		output['heading_magnetic'] = params[1]
		
		return output
	
	#HDT Heading - True
	def parse_HDT(self, params, output = {}):
		output['heading_true'] = params[1]
		
		return output

	#HSC Heading Steering Command
	def parse_HSC(self, params, output = {}):
		output['heading_true'] = params[1]
		output['heading_magnetic'] = params[3]
		
		return output
	
	#LCD Loran-C Signal Data
	def parse_LCD(self, params, output = {}):
		output['gri_microseconds'] = params[1]
		output['master_relative_snr'] = params[2]
		output['master_relative_ecd'] = params[3]
		output['time_difference'] = []
		for i in range(0, 5):
			diff = {}
			diff['microseconds'] = params[4+i*2]
			diff['signal_status'] = params[5+i*2]
			output['time_difference'].append(diff)
		
		return output

	#MSK MSK Receiver Interface (for DGPS Beacon Receivers)
	def parse_MSK(self, params, output = {}):
		output['frequency_khz'] = params[1]
		output['frequency_selection'] = params[2]
		output['msk_bit_rate'] = params[3]
		output['bit_rate_selection'] = params[4]
		output['pop_status'] = params[5]
		
		return output

	#MTW Water Temperature
	def parse_MTW(self, params, output = {}):
		output['temperature'] = params[1]
		return output

	#MWV Wind Speed and Angle
	def parse_MWV(self, params, output = {}):
		output = {}

		angle = float(params[1])
		if angle > 180:
			angle = 360 - angle
		if params[2] == 'R':
			output['awa'] = angle
			output['aws'] = float(params[3])
		elif params[2] == 'T':
			output['twa'] = angle
			output['tws'] = float(params[3])

		return output

	#MWD Wind Direction & Speed
	def parse_MWD(self, params, output = {}):
		output['twd_true'] = params[1]
		output['twd_magnetic'] = params[3]
		output['tws'] = params[5]

		return output

	#OSD Own Ship Data
	def parse_OSD(self, params, output = {}):
		output['heading_true'] = params[1]
		output['vessel_course'] = params[3]
		output['vessel_speed'] = params[5]

		return output
	
	#ROO Waypoints in Active Route
		wpts = []
		for i in range(len(params) - 1):
			wpts.append(params[i+i])
		output['waypoints'] = wpts

		return output
	
	#RMA Recommended Minimum Navigation Information
	
	
	#RMB Recommended Minimum Navigation Information
	def parse_RMB(self, params, output = {}):
		output['xte'] = float(params[2])
		if params[4] == 'L':
			output['xte'] = -output['xte']
		
		output['to_waypoint_id'] = params[4]
		output['from_waypoint_id'] = params[5]

		output['destination_latitude'] = self.parse_latitude(params[6], params[7])
		output['destination_longitude'] = self.parse_longitude(params[8], params[9])

		output['distance_to_destination'] = params[10]
		output['bearing_to_destination'] = params[11]
		output['vmg_destination'] = params[12]
		
		output['arrival_status'] = (params[13] == 'A')

		return output

	#RMC Recommended Minimum Navigation Information
	def parse_RMC(self, params, output = {}):

		output['latitude'] = self.parse_latitude(params[3], params[4])
		output['longitude'] = self.parse_longitude(params[5], params[6])

		#parse our date
		mydate = params[9]
		myday = int(mydate[0:2])
		mymonth = int(mydate[2:4])
		myyear = int('20' + mydate[4:6])

		#parse our time
		mytime = params[1]
		myhours = int(mytime[0:2])
		myminutes = int(mytime[2:4])
		myseconds = int(mytime[4:6])

		#make our timestamp
		dt = datetime.datetime(myyear, mymonth, myday, myhours, myminutes, myseconds)
		output['timestamp'] = dt.isoformat()

		#these are totally just guesses
		output['sog'] = params[7]
		
		return output

	#ROT Rate Of Turn
	#RPM Revolutions
	#RSA Rudder Sensor Angle

	#RSD RADAR System Data
	def parse_RSD(self, params, output = {}):
		output['cursor_range'] = params[9]
		output['cursor_bearing'] = params[10]
		output['range_scale'] = params[11]
		output['range_units'] = params[12]
		
		return output
	
	#RTE Routes
	#SFI Scanning Frequency Information
	#STN Multiple Data ID

	#TLL Target Latitude and Longitude
	def parse_TLL(self, params, output = {}):
		output['target_number'] = params[1]
		output['latitude'] = self.parse_latitude(params[2], params[3])
		output['longitude'] = self.parse_longitude(params[4], params[5])
		output['target_name'] = params[6]
		output['utc_time'] = params[7]
		
		return output
	
	#TTM Tracked Target Message
	def parse_TTM(self, params, output = {}):
		output['target_number'] = params[1]
		output['target_distance'] = params[2]
		output['target_bearing'] = params[3]
		output['target_speed'] = params[5]
		output['target_course'] = params[6]
		output['cpa'] = params[8]
		output['tcpa'] = params[9]
		output['target_name'] = params[11]
		output['target_status'] = params[12]
		output['reference_target'] = params[13]
		
		return output
	
	#VBW Dual Ground/Water Speed
	#VDR Set and Drift
	
	#VHW Water Speed and Heading
	def parse_VHW(self, params, output = {}):
		output['heading_magnetic'] = params[1]
		output['heading_true'] = params[3]
		output['water_speed'] = params[5]
		
		return output
	
	#VLW Distance Traveled through Water
	def parse_VLW(self, params, output = {}):
		output['log_total'] = params[1]
		output['log_water'] = params[3]

		#seems B&G adding extra params...
		if len(params) >= 6:
			output['log_trip'] = params[5]
		
		return output
	
	#VPW Speed - Measured Parallel to Wind
	
	#VTG Track Made Good and Ground Speed
	def parse_VTG(self, params, output = {}):
		output['cog_true'] = params[1]
		output['cog_magnetic'] = params[3]
		output['sog'] = params[5]

		return output	
		
	#VWR Relative Wind Speed and Angle
	#WCV Waypoint Closure Velocity
	#WNC Distance - Waypoint to Waypoint
	#WPL Waypoint Location
	
	#XDR Cross Track Error - Dead Reckoning
	def parse_XDR(self, params, output = {}):
		output['transducers'] = []

		devices = int(math.floor(len(params) / 4))
		for i in range(devices):
			transducer = {}
			transducer['type'] = params[1+i*4]
			transducer['data'] = params[2+i*4]
			transducer['units'] = params[3+i*4]
			transducer['name'] = params[4+i*4]

			output['transducers'].append(transducer)
		
		return output

	#XTE Cross-Track Error - Measured
	def parse_XTE(self, params, output = {}):
		output['xte'] = float(params[3])
		if params[4] == 'L':
			output['xte'] = -output['xte']
		
		return output

	#XTR Cross Track Error - Dead Reckoning

	#ZDA Time & Date - UTC, Day, Month, Year and Local Time Zone
	def parse_ZDA(self, params, output = {}):
		#parse our date
		myday = int(params[2])
		mymonth = int(params[3])
		myyear = int(params[4])

		#parse our time
		mytime = params[1]
		myhours = int(mytime[0:2])
		myminutes = int(mytime[2:4])
		myseconds = int(mytime[4:6])

		#make our timestamp
		dt = datetime.datetime(myyear, mymonth, myday, myhours, myminutes, myseconds)
		output['timestamp'] = dt.isoformat()
		
		return output
		
	#ZFO UTC & Time from Origin Waypoint
	#ZTG UTC & Time to Destination Waypoint

	def parse_latitude(self, latitude, northsouth):
		if latitude:
			lat = float(latitude) / 100.0
			if northsouth == 'S':
				lat = -lat
			
			return lat
		else:
			return 0.0

	def parse_longitude(self, longitude, eastwest):
		if longitude:
			lon = float(longitude) / 100.0
			if eastwest == 'W':
				lon = -lon
			
			return lon
		else:
			return 0.0

	def verifyline(self, line):

		#no blanks.
		if line.strip() == '':
			return False
			
		#has to start with a $
		if line[0] != '$':
			return False
			
		#make sure we have a checksum
		if line[-3:-2] == '*':
			target_checksum = line[-2:]
			check_line = bytearray(line[1:-3], 'ascii')
			
			#checksum is the hexadecimal value of an XOR of all chars between $ and *
			checksum = 0
			for i in range(0, len(check_line)):
				char = check_line[i]
				checksum = checksum ^ char
			checksum_hex = "{:02X}".format(int(checksum))	
			
			return target_checksum == checksum_hex
		else:
			return False