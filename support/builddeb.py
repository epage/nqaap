#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; version 2 only.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import os
import sys

import py2deb


def build_package(distribution):
	py2deb.Py2deb.SECTIONS = py2deb.SECTIONS_BY_POLICY[distribution]
	try:
		os.chdir(os.path.dirname(sys.argv[0]))
	except:
		pass

	p=py2deb.Py2deb("nqaap")
	p.prettyName="NQA Audiobook Player"
	p.description="""Very simple Audiobook player.
Supports playing, pausing, seeking (sort of) and saving state when changing book/closing.
Plays books arranged as dirs under myDocs/Audiobooks
.
Homepage: http://wiki.maemo.org/Nqaap"""
	p.author="Soeren 'Pengman' Pedersen"
	p.mail="pengmeister@gmail.com"
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
	p.icon = {
		"debian": "src/usr/share/icons/hicolor/26x26/hildon/nqaap.png",
		"diablo": "src/usr/share/icons/hicolor/26x26/hildon/nqaap.png",
		"fremantle": "src/usr/share/icons/hicolor/48x48/hildon/nqaap.png",
	}[distribution]
	p.arch="all"
	p.urgency="low"
	p.distribution=distribution
	p.repository="extras"
	p.bugTracker="https://bugs.maemo.org/enter_bug.cgi?product=nQa%%20Audiobook%%20Player"
	p.postinstall="""#!/bin/sh
rm -f ~/.nqaap/nqaap.log
"""
	version = "0.8.7"
	build = "0"
	changeloginformation = """
* Fixing a bug with initially configuring the book location
""".strip()
	dir_name = "src"
	#Thanks to DareTheHair from talk.maemo.org for this snippet that
	#recursively builds the file list
	for root, dirs, files in os.walk(dir_name):
		if any(f.startswith(".") for f in root.split(os.sep)):
			continue # avoid hidden folders, esp svn ones

		real_dir = root[len(dir_name):]
		fake_file = []
		for f in files:
			fake_file.append(root + os.sep + f + "|" + f)
		if len(fake_file) > 0:
			p[real_dir] = fake_file

	print p
	if distribution == "debian":
		print p.generate(
			version="%s-%s" % (version, build),
			changelog=changeloginformation,
			build=True,
			tar=False,
			changes=False,
			dsc=False,
		)
	else:
		print p.generate(
			version="%s-%s" % (version, build),
			changelog=changeloginformation,
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
