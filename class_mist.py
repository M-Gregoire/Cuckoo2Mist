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

# Takes the json and create the mist !
class mistit(object):

	def __init__(self, input_file, elements2mist, types2mist):
		self.infile = input_file
		print('Generating MIST report for "%s"...' % self.infile)
		#self.skiplist = []
		#self.ip_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
		self.errormsg = ''
		self.mist = StringIO()
		self.elements2mist = elements2mist
		self.types2mist = types2mist
		self.cache = {}
		self.missing = {}
		self.behaviour_report = ''

	# Open the json report in behaviour_report and returns true if it suceeded
	def parse(self):
		if not os.path.exists(self.infile) and not os.path.exists(self.infile+".gz"):
			self.errormsg = 'Behaviour report does not exist.'
			return False
		try:
			json_data=open(self.infile, "r")
			self.behaviour_report = json.load(json_data)

			return True
		except Exception as e:
			self.errormsg = 'Could not parse the behaviour report. (%s)' % e
			return False		

	# Write the mist report in outputfile. Returns true if it suceeded
	def write(self, outputfile):
		try:
			w_file = file(outputfile, 'w')
			w_file.write(self.mist.getvalue())
			w_file.flush()
			w_file.close()
		except Exception as e:
			self.errormsg = e
			return False
		return True


	#def ELFHash(self, key):
	#	hash = 0
	#	x    = 0
	#	for i in range(len(key)):
	#		hash = (hash << 4) + ord(key[i])
	#		x = hash & 0xF0000000
	#		if x != 0:
	#			hash ^= (x >> 24)
	#		hash &= ~x
	#	return hash              

	#def int2hex(self, n, len):
	#	assert n   is not None
	#	assert len is not None
	#	try:
	#		hexval = ('0' * len) + "%x" % int(n)
	#	except ValueError:
	#		hexval = ('0' * len) + "%x" % int(n, 16)	
	#	return hexval[len * -1:]
	
	def convert2mist(self, value):
		val_low = value.lower()
		try:
			return self.cache[val_low]
		except:
			res 	= self.ELFHash(val_low)
			result 	= self.int2hex(res, 8)
			self.cache[val_low] = result
		return result
		
	def splitfilename(self, fname):
		pattern  = '(\"?(.*)\\\\([^\\/:?<>"|\s]+)\.([^\\/:?<>"|\s,-]{1,4})\"?(.*))|'
		pattern += '(\"?(.*)\\\\([^\\/:?<>"|\s]+)\"?(.*))|'
		pattern += '(\"?([^\\/:?<>"|\s]+)\.([^\\/:?<>"|\s,-]{1,4})\"?(.*))|'
		pattern += '(\"?([^\\/:?<>"|\s-]+)\"?(.*))'
		fname = fname.lower()
		m = re.search(pattern, fname)
		if m:
			if m.group(1) != None:	
				path 		= m.group(2)
				filename 	= m.group(3)
				extension 	= m.group(4)
				parameter 	= m.group(5)
			elif m.group(6) != None:
				path 		= m.group(7)
				filename 	= m.group(8)
				extension 	= ''
				parameter 	= m.group(9)
			elif m.group(10) != None:
				path 		= ''
				filename 	= m.group(11)
				extension 	= m.group(12)
				parameter 	= m.group(13)
			elif m.group(14) != None:
				path 		= ''
				filename 	= m.group(15)
				extension 	= ''
				parameter 	= m.group(16)
		else:
			path 		= ''
			filename 	= fname
			extension 	= ''
			parameter 	= ''
		return extension, path, filename, parameter
	
	def file2mist(self, value, full):
		(extension, path, filename, parameter) = self.splitfilename(value)	
		mypath      = self.convert2mist(path)
		myextension = self.convert2mist(extension)
		if full:
			myfilename  = self.convert2mist(filename)
			myparameter = self.convert2mist(parameter)
			return myextension + ' ' + mypath + ' ' + myfilename + ' ' + myparameter
		else:
			return myextension + ' ' + mypath
	
	
		
	def convert_thread(self, pid, tid, api_calls):
		self.mist.write( '# process ' + str(pid) + ' thread ' + str(tid) + ' #\n' )
		for api_call in api_calls:
			arguments 	= api_call['arguments']
			category 	= api_call['category']
			api 		= api_call['api']
			if not 3 == 4: #operation_node.tag in self.skiplist:
				values = ""
				category_node = self.elements2mist.find(".//" + category)
				if category_node == None:
					self.missing[category] = 1
					continue
				self.mist.write( category_node.attrib["mist"] + " " )
				translate_node = self.elements2mist.find(".//" + api)
				if translate_node == None:
					self.missing[api] = 1
					continue
				self.mist.write( translate_node.attrib["mist"] + " |" )
				for attrib_node in translate_node.getchildren():
					value = self.types2mist.find(attrib_node.attrib["type"]).attrib["default"]
		# There is something to do here
					#for arg in api_call["arguments"]:
						#if arg["name"] == attrib_node.tag:
					for arg in arguments:
						if arg[1] == attrib_node.tag:
							value = self.convertValue(attrib_node.attrib["type"], arg["value"], attrib_node.tag)
					self.mist.write( " " + value )
				self.mist.write( '\n' )
		return True
	
	def convertValue(self, ttype, value, name):
		result = 'QQQQQQQQ' + value
		if ttype == 'type_string':
			result = self.convert2mist(value)		
		elif ttype == 'type_hex':
			result = value[2:10]
			while len(result) < 8:
				result = "0" + result 			
		elif ttype == 'type_integer':
			result = self.int2hex(value, 8)
		return result

	
	def convert(self):
		processes = {}
		procs = self.behaviour_report['behavior']['processes']
		for proc in procs:
			process_id = proc['pid']
			parent_id = proc['ppid']
			process_name = proc['process_name']
			calls = proc['calls']
			threads = {}
			for call in calls:
				thread_id = call['tid']
				try:
					threads[thread_id].append(call)	
				except:
					threads[thread_id] = []
					threads[thread_id].append(call)
			
			processes[process_id] = {}
			processes[process_id]["parent_id"] = parent_id 
			processes[process_id]["process_name"] = process_name 
			processes[process_id]["threads"] = threads 
			
		for p_id in processes:
			for t_id in processes[p_id]["threads"]:
				self.convert_thread(p_id, t_id, processes[p_id]["threads"][t_id])

		if len(self.missing.keys()) > 0:
			self.errormsg = "Warning: %s - %s not in elements2mist." % (self.infile, ", ".join(self.missing.keys()))

		return True


if __name__ == '__main__':
	elements2mist.parse("conf/cuckoo_elements2mist_leveled.xml")
	types2mist = ET.ElementTree()
	types2mist.parse("conf/cuckoo_types2mist.xml")
	x = mistit('reports/report.json', elements2mist, types2mist)
	if x.parse() and x.convert():
		x.write('report/report.mist')
	else:
		print(x.errormsg)
	
 
