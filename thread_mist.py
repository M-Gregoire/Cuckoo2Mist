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


import sys
import os
from threading import Thread   
import subprocess
from class_mist import mistit
import gzip

import logging as log

class th_seq2mist(Thread):
	# This thread converts a new sectional XML report in a MIST report
	def __init__(self, input_file, elements2mist, types2mist, analysis_id):
		Thread.__init__(self)
		self.input_file = input_file
		# froot : folder/reportXX
		# fext : .json
		(froot, fext) = os.path.splitext(self.input_file)
		self.elements2mist = elements2mist
		self.types2mist = types2mist
		self.analysis_id = analysis_id
		self.output_file = froot + ".mist"

	# Log in report2mist.log the msg passed as argument
	def log(self, msg):
		# Fullmsg = folder/name.json: msg
		fullmsg = "%s: %s\n" % (self.input_file, msg)

		log_path = "logs/report2mist.log"
		# Create folder if does not exist
		if not os.path.exists(os.path.dirname(log_path)):
			os.mkdirs(os.path.dirname(log_path))

		# Option a : append
		hfile = open(log_path, "a")
		hfile.write(fullmsg)
		hfile.close()

	def run(self):
		mist = mistit(self.input_file, self.elements2mist, self.types2mist)
		if mist.parse() and mist.convert():
			mist.write(self.output_file)
			self.log(mist.errormsg)
			log.info("Thread terminé")
		else:
			self.log(mist.errormsg)
