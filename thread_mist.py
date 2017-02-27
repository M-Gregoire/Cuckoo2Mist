#!/usr/bin/env python
# encoding: utf-8
"""
thread_mist.py

Created by Philipp Trinius on 2013-11-10.
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


import sys
import os
from threading import Thread   
import subprocess
from class_mist import mistit
import gzip

class th_seq2mist(Thread):
	"""This thread converts a new sectional XML report in a MIST report"""

	def __init__(self, input_file, elements2mist, types2mist, analysis_id):
		Thread.__init__(self)
		self.input_file = input_file
		(froot, fext) = os.path.splitext(self.input_file)
		self.elements2mist = elements2mist
		self.types2mist = types2mist
		self.analysis_id = analysis_id
		self.output_file = froot + ".mist"

	def log(self, msg):
#		msg = msg.strip()
		fullmsg = "%s: %s\n" % (self.input_file, msg)
		hfile = open("log/report2mist.log", "a")
		hfile.write(fullmsg)
		hfile.close()

	def run(self):
		mist = mistit(self.input_file, self.elements2mist, self.types2mist)
		if mist.parse() and mist.convert():
			mist.write(self.output_file)
#			if len(mist.errormsg) > 0:
			self.log(mist.errormsg)
		else:
			self.log(mist.errormsg)
