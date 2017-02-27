#!/usr/bin/env python
# encoding: utf-8
"""
cuckoo2mist.py

Created by Dr. Philipp Trinius on 2013-11-10.
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

__author__ = "philipp trinius"
__version__ = "0.2"



import re
import os, sys
import getopt
import subprocess
import time
import hashlib
import xml.etree.ElementTree as ET
import glob

from thread_mist import th_seq2mist

max_threads	= 10
user_interrupt	= False

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def get_log_md5s():
	result = {}
	for f in os.listdir('log'):
		hfile = open(os.path.join('log', f), "r")
		h = hashlib.sha1()
		h.update(hfile.read())
		result[f] = h.hexdigest()
		hfile.close()
	return result

def read_configuration(fconfigdir):
	elements2mist = ET.ElementTree()
	elements2mist.parse(os.path.join(fconfigdir, "cuckoo_elements2mist.xml"))

	types2mist = ET.ElementTree()
	types2mist.parse(os.path.join(fconfigdir, "cuckoo_types2mist.xml"))	
	return elements2mist, types2mist

def generate_Mist_Reports(files, e2m, t2m):
	global max_threads
	### Determine the IDs of analysis that yet not have been converted ########################################
	seqReportRows = []
	for ffile in files:
		seqReportRows.append({'analysis_id': None, 'seq_path': ffile})

	### Convert reports to MIST representation (in threads) ####################################
	thlist = []
	try:
		for seqReportRow in seqReportRows:
			while len(thlist) >= max_threads:
				time.sleep(5)
				for t in thlist:
					t.join(2.0)
					if not t.isAlive():
						thlist.remove(t)
			t = th_seq2mist(input_file=seqReportRow["seq_path"], elements2mist=e2m, types2mist=t2m, analysis_id=seqReportRow["analysis_id"])
			thlist.append(t)
			t.start()
	except KeyboardInterrupt:
		pass
	print '\nAborting %s threads...' % len(thlist)
	for t in thlist:
		t.join()
		thlist.remove(t)
		print '  Aborted one thread - %s remaining' % len(thlist)
		sys.stdout.flush()
	print "  --> All threads aborted\n"



def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hcio:v", ["help", "config_dir=", "input="])
		except getopt.error, msg:
			raise Usage(msg)
			
		workdir = sys.path[0]
		os.chdir(workdir)
		
		f_configdir = "conf"
		
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-o", "--config"):
				f_configdir = value
			if option in ("-i", "--input"):
				f_input = value
				
		print "Reading configuration files from %s ..." % (f_configdir), 
		(e2m, t2m) = read_configuration(f_configdir)
		print " done."
		
		log_md5s_before = get_log_md5s()
		
		print "Reading %s" % (f_input),
		files = []
		if os.path.exists(f_input):
			for ffile in os.listdir(f_input):
				file = os.path.join(f_input, ffile)
				if os.path.isfile(file) and file.endswith(".json"):
					files.append(file)
					print ".",
		if len(files) == 0:
			# no reports found
			print "No reports found."
			sys.exit(1)
		else:
			print " done."
			
		generate_Mist_Reports(files, e2m, t2m)
							
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())

