#!/usr/bin/env python

import os
import sys

try:
	import py2deb
except ImportError:
	import fake_py2deb as py2deb

import constants


__app_name__ = constants.__app_name__
__description__ = """Very simple Audiobook player.
Supports playing, pausing, seeking (sort of) and saving state when changing book/closing.
Plays books arranged as dirs under myDocs/Audiobooks
.
Homepage: http://wiki.maemo.org/Nqaap"""
__author__ = "Soeren 'Pengman' Pedersen"
__email__ = "pengmeister@gmail.com"
__version__ = constants.__version__
__build__ = constants.__build__
__changelog__ = """
* Fixing some packaging bugs I made that broke everything
""".strip()


__postinstall__ = """#!/bin/sh -e

gtk-update-icon-cache -f /usr/share/icons/hicolor
rm -f ~/.%(name)s/%(name)s.log
""" % {"name": constants.__app_name__}


def find_files(prefix, path):
	for root, dirs, files in os.walk(path):
		for file in files:
			if file.startswith(prefix+"-"):
				fileParts = file.split("-")
				unused, relPathParts, newName = fileParts[0], fileParts[1:-1], fileParts[-1]
				assert unused == prefix
				relPath = os.sep.join(relPathParts)
				yield relPath, file, newName


def unflatten_files(files):
	d = {}
	for relPath, oldName, newName in files:
		if relPath not in d:
			d[relPath] = []
		d[relPath].append((oldName, newName))
	return d


def build_package(distribution):
	try:
		os.chdir(os.path.dirname(sys.argv[0]))
	except:
		pass

	py2deb.Py2deb.SECTIONS = py2deb.SECTIONS_BY_POLICY[distribution]
	p = py2deb.Py2deb(__app_name__)
	p.prettyName = constants.__pretty_app_name__
	p.description = __description__
	p.bugTracker="https://bugs.maemo.org/enter_bug.cgi?product=nQa%%20Audiobook%%20Player"
	p.author = __author__
	p.mail = __email__
	p.license = "lgpl"
	p.depends = ", ".join([
		"python2.6 | python2.5",
		"python-gtk2 | python2.5-gtk2",
		"python-dbus | python2.5-dbus",
		"python-telepathy | python2.5-telepathy",
		"python-gobject | python2.5-gobject",
		"python-simplejson",
	])
	maemoSpecificDepends = ", python-osso | python2.5-osso, python-hildon | python2.5-hildon"
	p.depends += {
		"debian": ", python-gst0.10",
		"diablo": maemoSpecificDepends,
		"fremantle": maemoSpecificDepends + ", python-gst0.10",
	}[distribution]
	p.section = {
		"debian": "sound",
		"diablo": "user/multimedia",
		"fremantle": "user/multimedia",
	}[distribution]
	p.arch="all"
	p.urgency="low"
	p.distribution=distribution
	p.repository="extras"
	p.changelog = __changelog__
	p.postinstall = __postinstall__
	p.icon = {
		"debian": "26x26-%s.png" % constants.__app_name__,
		"diablo": "26x26-%s.png" % constants.__app_name__,
		"fremantle": "48x48-%s.png" % constants.__app_name__,
	}[distribution]
	p["/opt/%s/bin" % constants.__app_name__] = [ "%s.py" % constants.__app_name__ ]
	for relPath, files in unflatten_files(find_files("src", ".")).iteritems():
		fullPath = "/opt/%s/lib" % constants.__app_name__
		if relPath:
			fullPath += os.sep+relPath
		p[fullPath] = list(
			"|".join((oldName, newName))
			for (oldName, newName) in files
		)
	p["/usr/share/applications/hildon"] = ["%s.desktop" % constants.__app_name__]
	p["/usr/share/icons/hicolor/26x26/hildon"] = ["26x26-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]
	p["/usr/share/icons/hicolor/48x48/hildon"] = ["48x48-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]
	p["/usr/share/icons/hicolor/64x64/hildon"] = ["64x64-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]
	p["/usr/share/icons/hicolor/scalable/hildon"] = ["scale-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]

	print p
	if distribution == "debian":
		print p.generate(
			version="%s-%s" % (__version__, __build__),
			changelog=__changelog__,
			build=True,
			tar=False,
			changes=False,
			dsc=False,
		)
	else:
		print p.generate(
			version="%s-%s" % (__version__, __build__),
			changelog=__changelog__,
			build=False,
			tar=True,
			changes=True,
			dsc=True,
		)
	print "Building for %s finished" % distribution


if __name__ == "__main__":
	if len(sys.argv) == 1:
		distribution = "fremantle"
	else:
		distribution = sys.argv[1]
	build_package(distribution)
