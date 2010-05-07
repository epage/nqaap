#!/usr/bin/env python

import os
import logging

import constants
import nqaap_gtk


_moduleLogger = logging.getLogger(__name__)


try:
	os.makedirs(constants._data_path_)
except OSError, e:
	if e.errno != 17:
		raise

logging.basicConfig(level=logging.DEBUG, filename=constants._user_logpath_)
_moduleLogger.info("%s %s-%s" % (constants.__pretty_app_name__, constants.__version__, constants.__build__))
_moduleLogger.info("OS: %s" % (os.uname()[0], ))
_moduleLogger.info("Kernel: %s (%s) for %s" % os.uname()[2:])
_moduleLogger.info("Hostname: %s" % os.uname()[1])

try:
	nqaap_gtk.run()
finally:
	logging.shutdown()
