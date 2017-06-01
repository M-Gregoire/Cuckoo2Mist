#!/usr/bin/env python
# encoding: utf-8
"""
cuckoo2mist.py

Created by Dr. Philipp Trinius on 2013-11-10.
Modified by Grégoire Martinache on 2017-02

Copyright (c) 2013 pi-one.net . 

This program is free software; you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your option) 
any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
more details.

You should have received a copy of the GNU General Public License along with 
this program; if not, see <http://www.gnu.org/licenses/>
"""

__author__ = "philipp trinius & gregoire martinache"
__license__ = "GPL"
__version__ = "0.3"

import os
import sys
import re
import xml.etree.cElementTree as ET
import mistSplit as mysplit
from io import StringIO
import gzip
import json

import logging as log

# Takes the json and create the mist !
class mistit(object):

	def __init__(self, input_file, elements2mist, types2mist):
		self.infile = input_file
		log.info('Generating MIST report for "%s"...' % self.infile)
		#self.skiplist = []
		#self.ip_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
		#self.errormsg = ''
		#self.mist = StringIO()
		self.elements2mist = elements2mist
		self.types2mist = types2mist
		# Cache used for hashing
		self.cache = {}
		# Used for warning when a category or API is find in the JSON report but not in the XML
		self.missingApi = {}
		self.missingCategory = {}
		# The json report to convert
		self.behaviour_report = ''
		# This will be written in the report file
		self.mist_report = ''

	# Open the json report in behaviour_report and returns true if it suceeded
	def parse(self):
		if not os.path.exists(self.infile) and not os.path.exists(self.infile+".gz"):
			log.error('Behaviour report does not exist.')
			return False
		try:
			json_data=open(self.infile, "r")
			self.behaviour_report = json.load(json_data)
			return True
		except Exception as e:
			log.error('Could not parse the behaviour report. '+e)
			return False		

	# Write the mist report in outputfile. Returns true if it suceeded
	def write(self, outputfile):
		log.info("Writing report to : "+outputfile)
		f = open(outputfile, 'w')
		f.write(self.mist_report)
		return True

	# Add something to the report which will be written to a file at the end of the thread
	def addToReport(self, msg):
		self.mist_report+=msg
		return True

	############################################
	############ Hash calculations #############
	############################################

	def ELFHash(self, key):
		hash = 0
		x    = 0
		for i in range(len(key)):
			hash = (hash << 4) + ord(key[i])
			x = hash & 0xF0000000
			if x != 0:
				hash ^= (x >> 24)
			hash &= ~x
		return hash              

	def int2hex(self, n, len):
		assert n   is not None
		assert len is not None
		try:
			hexval = ('0' * len) + "%x" % int(n)
		except ValueError:
			hexval = ('0' * len) + "%x" % int(n, 16)	
		return hexval[len * -1:]
	
	def convert2mist(self, value):
		val_low = value.lower()
		try:
			return self.cache[val_low]
		except:
			res 	= self.ELFHash(val_low)
			result 	= self.int2hex(res, 8)
			self.cache[val_low] = result
		return result
		
	############################################

	#def splitfilename(self, fname):
	#	pattern  = '(\"?(.*)\\\\([^\\/:?<>"|\s]+)\.([^\\/:?<>"|\s,-]{1,4})\"?(.*))|'
	#	pattern += '(\"?(.*)\\\\([^\\/:?<>"|\s]+)\"?(.*))|'
	#	pattern += '(\"?([^\\/:?<>"|\s]+)\.([^\\/:?<>"|\s,-]{1,4})\"?(.*))|'
	#	pattern += '(\"?([^\\/:?<>"|\s-]+)\"?(.*))'
	#	fname = fname.lower()
	#	m = re.search(pattern, fname)
	#	if m:
	#		if m.group(1) != None:	
	#			path 		= m.group(2)
	#			filename 	= m.group(3)
	#			extension 	= m.group(4)
	#			parameter 	= m.group(5)
	#		elif m.group(6) != None:
	#			path 		= m.group(7)
	#			filename 	= m.group(8)
	#			extension 	= ''
	#			parameter 	= m.group(9)
	#		elif m.group(10) != None:
	#			path 		= ''
	#			filename 	= m.group(11)
	#			extension 	= m.group(12)
	#			parameter 	= m.group(13)
	#		elif m.group(14) != None:
	#			path 		= ''
	#			filename 	= m.group(15)
	#			extension 	= ''
	#			parameter 	= m.group(16)
	#	else:
	#		path 		= ''
	#		filename 	= fname
	#		extension 	= ''
	#		parameter 	= ''
	#	return extension, path, filename, parameter
	
	#def file2mist(self, value, full):
	#	(extension, path, filename, parameter) = self.splitfilename(value)	
	#	mypath      = self.convert2mist(path)
	#	myextension = self.convert2mist(extension)
	#	if full:
	#		myfilename  = self.convert2mist(filename)
	#		myparameter = self.convert2mist(parameter)
	#		return myextension + ' ' + mypath + ' ' + myfilename + ' ' + myparameter
	#	else:
	#		return myextension + ' ' + mypath
	
	
	# Converts a thread section in the JSON to mist	
	def convert_thread(self, pid, tid, api_calls):
		self.addToReport( '# process ' + str(pid) + ' thread ' + str(tid) + ' #\n' )
		for api_call in api_calls:
			
			arguments 	= api_call['arguments']
			category 	= api_call['category']
			api 		= api_call['api']
			values = ""

			typeFound=False
			# Find the corresponding category node in the XML
			category_node = self.elements2mist.find(".//" + category)
			if category_node == None:
				self.missingCategory[category] = 1
				continue

			# Find the corresponding api node in the XML
			api_node = self.elements2mist.find(".//" + api)
			if api_node == None:
				self.missingApi[api] = category
				continue

			# Write in the report the category node code (cf mist format)
			self.addToReport( category_node.attrib["mist"] + " " )
			# addToReport in the report the api node code (cf mist format)
			self.addToReport( api_node.attrib["mist"] + " |" )

			# For every arguments...
			for key,val in arguments.items():
				# We try to find the the corresponding type in the XML						
				for attrib_node in api_node.getchildren():			
					if key == attrib_node.tag:
						typeFound=True
						break
				# If we found the correct entry in the XML, we generate the mist's line report
				if(typeFound):
					# Type of the entry (String, hex or integer)
					valType=attrib_node.attrib["type"]
					# Value of the entry
					valKey = str(val)
					# We convert the value to MIST argument
					success = False
					valConv,success = self.convertValue(valType, valKey)
					self.addToReport(" "+valConv)
					# If conversion failed, show the unknow type to help debug
					if(not success):
						log.warning("Unknow type found : "+valType)

				# If entry not found, warning message so the user can add it to the XML
				else:
					log.warning("A key seems to be missing in the cuckoo_elements2mist.xml. See readme.md for informations.")
					log.warning("Cat: "+category+ " - Api : " + api + " - Key : " + key +" - Value : "+str(val))
			
			self.addToReport( '\n' )
		return True
	
	# Call the correct hashing function depending on the type
	def convertValue(self, ttype, value):
		result = 'QQQQQQQQ' + value
		success = False
		if ttype == 'type_string':
			result = self.convert2mist(value)	
			success = True
		elif ttype == 'type_hex':
			result = value[2:10]
			while len(result) < 8:
				result = "0" + result	
			success = True	
		elif ttype == 'type_integer':
			result = self.int2hex(value, 8)
			success = True
		else:
			log.warning("An unknow type has been detected in the XML file. Argument ignored")
			result = "00000000"
		return result, success

	# Launch the conversion on all threads in the JSON
	def convert(self):
		processes = {}
		procs = self.behaviour_report['behavior']['processes']
		for proc in procs:
			process_id = proc['pid']
			parent_id = proc['ppid']
			process_name = proc['process_name']
			calls = proc['calls']
			# Create a dictionnary of threads
			# The key is the n° of the thread
			# The content is all calls he makes
			threads = {}
			for call in calls:
				thread_id = call['tid']
				try:
					threads[thread_id].append(call)	
				except:
					threads[thread_id] = []
					threads[thread_id].append(call)
			
			# Create a dictionnary of process
			# The key is the n° of the process
			processes[process_id] = {}
			processes[process_id]["parent_id"] = parent_id 
			processes[process_id]["process_name"] = process_name 
			processes[process_id]["threads"] = threads 
			
		# For all processes...
		for p_id in processes:
			# For each threads of those processes...
			for t_id in processes[p_id]["threads"]:
				# Convert the thread
				self.convert_thread(p_id, t_id, processes[p_id]["threads"][t_id])

		if len(self.missingCategory.keys()) > 0:
			for key,val in self.missingCategory.items():
				log.warning("Category <"+key+"> does not exists in the XML")
		if len(self.missingApi.keys()) > 0:
			for key,val in self.missingApi.items():
				log.warning("The category <"+val+"> does not contains an API named <"+key+"> in the XML")

		return True


if __name__ == '__main__':
	elements2mist.parse("conf/cuckoo_elements2mist_leveled.xml")
	types2mist = ET.ElementTree()
	types2mist.parse("conf/cuckoo_types2mist.xml")
	json = mistit('reports/report.json', elements2mist, types2mist)
	if json.parse() and json.convert():
		log.info('Report generated')
	else:
		log.error(json.errormsg)
	
 
