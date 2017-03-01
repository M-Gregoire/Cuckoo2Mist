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

import re
import os, sys
import argparse
import subprocess
import time
import hashlib
import xml.etree.ElementTree as ET
import glob

import logging as log

from thread_mist import th_seq2mist

# Max_threads used to convert json
max_threads	= 10
# Can user interrupt ?
user_interrupt	= False



# Handle errors
class ErrorClass(Exception):
	def __init__(self, msg):
		self.msg = msg

# Load config
def read_configuration(fconfigdir):
	elements2mist = ET.ElementTree()
	elements2mist.parse(os.path.join(fconfigdir, "cuckoo_elements2mist.xml"))

	types2mist = ET.ElementTree()
	types2mist.parse(os.path.join(fconfigdir, "cuckoo_types2mist.xml"))	
	return elements2mist, types2mist

# Generate mist reports based on the json reports and configs
def generate_Mist_Reports(files, e2m, t2m):
	global max_threads
	# Determine the IDs of analysis that yet not have been converted
	seqReportRows = []
	for ffile in files:
		seqReportRows.append({'analysis_id': None, 'seq_path': ffile})

	# Convert reports to MIST representation (in threads)
	# thlist : List of all threads
	thlist = []
	try:
		for seqReportRow in seqReportRows:
			# If there is too much threads running, we wait another thread finishes
			while len(thlist) >= max_threads:
				time.sleep(5)
				for t in thlist:
					t.join(2.0)
					if not t.isAlive():
						thlist.remove(t)
			# Open a new thread that will convert the json to mist
			t = th_seq2mist(input_file=seqReportRow["seq_path"], elements2mist=e2m, types2mist=t2m, analysis_id=seqReportRow["analysis_id"])
			thlist.append(t)
			t.start()

	except KeyboardInterrupt:
		pass



	#print('\nAborting %s threads...' % len(thlist))
	for t in thlist:
		t.join()
		thlist.remove(t)
		log.info('On thread has finished - %s remaining' % len(thlist))
		sys.stdout.flush()
	print("Cuckoo2Mist is done !")

#def main(argv=None):
def main():
	# Get arguments
	argv = sys.argv
	try:
		parser = argparse.ArgumentParser()
		parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose mode')
		parser.add_argument('-i', '--input', dest='input', default='reports', help='Specify where are the reports')
		parser.add_argument('-o', '--config', dest='config', default='conf', help='Specify where are the configs')
		args = parser.parse_args()
		
		if args.verbose:
			log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
			log.info("Verbose output.")
		else:
			log.basicConfig(format="%l(levelname)s: %(message)s")
		f_configdir = args.config
		f_input = args.input

		# Workdir = directory where the script is
		workdir = sys.path[0]
		os.chdir(workdir)
				
		# e2m : Element2Mist // t2m : Types2mist
		log.info("Reading configuration files from %s/" % (f_configdir))
		(e2m, t2m) = read_configuration(f_configdir)
		log.info("Done.")
		
		# Get reports
		log.info("Reading reports from %s/" % (f_input))
		files = []
		if os.path.exists(f_input):
			for ffile in os.listdir(f_input):
				file = os.path.join(f_input, ffile)
				if os.path.isfile(file) and file.endswith(".json"):
					files.append(file)
		if len(files) == 0:
			log.error("No reports found.")
			sys.exit(1)
		else:
			log.info("%s reports read." % (len(files)))

		# Generate mist reports for each reports.json found		
		generate_Mist_Reports(files, e2m, t2m)
							
	except ErrorClass as err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

# Call main() and give the return code that is the result of main()
if __name__ == "__main__":
	print("Starting Cuckoo2Mist converter.")
	sys.exit(main())

