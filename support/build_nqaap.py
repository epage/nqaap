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
    print
    p=py2deb.Py2deb("nqaap") #This is the package name and MUST be in
                               #lowercase! (using e.g. "mClock" fails
                               #miserably...)
    p.prettyName="NQA Audiobook Player"
    p.description="""Very simple Audiobook player.
Supports playing, pausing, seeking (sort of) and saving state when changing book/closing.
Plays books arranged as dirs under myDocs/Audiobooks
.
Homepage: http://nqaap.garage.maemo.org/"""
    p.author="Soeren 'Pengman' Pedersen"
    p.mail="pengmeister@gmail.com"
    p.depends = ", ".join([
        "python2.6 | python2.5",
        "python-gtk2 | python2.5-gtk2",
        "python-dbus | python2.5-dbus",
        "python-telepathy | python2.5-telepathy",
        "python-gobject | python2.5-gobject",
        "python-gst0.10 | python2.5-gst0.10",
    ])
    maemoSpecificDepends = ", python-osso | python2.5-osso, python-hildon | python2.5-hildon"
    p.depends += {
        "debian": "",
        "diablo": maemoSpecificDepends,
        "fremantle": maemoSpecificDepends,
    }[distribution]
    p.section = {
        "debian": "sound",
        "diablo": "user/multimedia",
        "fremantle": "user/multimedia",
    }[distribution]
    p.icon = "src/usr/share/icons/hicolor/48x48/hildon/nqaap.png"
    p.arch="all"                #should be all for python, any for all arch
    p.urgency="low"             #not used in maemo onl for deb os
    p.distribution=distribution
    p.repository="extras"
    p.bugTracker="http://talk.maemo.org/showthread.php?p=619738"
    p.postinstall="""#!/bin/sh
rm -f ~/.nqaap/nqaap.log
"""
    #  p.postremove="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your post remove script
    #  p.preinstall="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your pre install script
    #  p.preremove="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your pre remove script
    version = "0.8.3"           #Version of your software, e.g. "1.2.0" or "0.8.2"
    build = "0" #Build number, e.g. "1" for the first build of this
                                #version of your software. Increment
                                #for later re-builds of the same
                                #version of your software.  Text with
                                #changelog information to be displayed
                                #in the package "Details" tab of the
                                #Maemo Application Manager
    changeloginformation = """
Fixing a crash on launch (Post 140)
""".strip()
    dir_name = "src" #Name of the subfolder containing your package
                                #source files
                                #(e.g. usr\share\icons\hicolor\scalable\myappicon.svg,
                                #usr\lib\myapp\somelib.py). We suggest
                                #to leave it named src in all projects
                                #and will refer to that in the wiki
                                #article on maemo.org
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
