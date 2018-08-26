#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import json
import codecs
from pathlib import Path
from lib.cuckoo.common.abstracts import Report
from lib.cuckoo.common.exceptions import CuckooReportError


class cuckoo2mist(Report):
	order=2
	# Save the report in Mist
	def run(self, results):
		print("Lecture du JSON")
		path = os.path.join(self.reports_path, "report.json")
		reportJSON = Path(path)
		if reportJSON.is_file():
			# Get script path in config
			CuckooConvert = self.options.get("script", "/")
			os.system(CuckooConvert+"cuckoo2mist.py -i"+self.reports_path)
