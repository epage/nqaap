#!/usr/bin/python2.5
 # -*- coding: utf-8 -*-
 ## This program is free software; you can redistribute it and/or modify
 ## it under the terms of the GNU General Public License as published
 ## by the Free Software Foundation; version 2 only.
 ##
 ## This program is distributed in the hope that it will be useful,
 ## but WITHOUT ANY WARRANTY; without even the implied warranty of
 ## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 ## GNU General Public License for more details.
 ##
import py2deb
import os
if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
    print
    p=py2deb.Py2deb("nqaap") #This is the package name and MUST be in
                               #lowercase! (using e.g. "mClock" fails
                               #miserably...)
    p.description="Very simple Audiobook player. \nSupports playing, pausing, seeking (sort of) and saving state when changing book/closing.\nPlays books arranged as dirs under myDocs/Audiobooks"
    p.author="Soeren 'Pengman' Pedersen"
    p.mail="pengmeister@gmail.com"
    p.depends = "python2.5, python2.5-gtk2, python-gst0.10"
    p.section="user/multimedia"
    p.icon = "/usr/share/icons/hicolor/48x48/hildon/nqaap.png"
    p.arch="all"                #should be all for python, any for all arch
    p.urgency="low"             #not used in maemo onl for deb os
    p.distribution="fremantle"
    p.repository="extras-devel"
    p.xsbc_bugtracker="http://talk.maemo.org/showthread.php?p=619738"
    #  p.postinstall="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your post install script
    #  p.postremove="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your post remove script
    #  p.preinstall="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your pre install script
    #  p.preremove="""#!/bin/sh
    #  chmod +x /usr/bin/mclock.py""" #Set here your pre remove script
    version = "0.8.0"           #Version of your software, e.g. "1.2.0" or "0.8.2"
    build = "2" #Build number, e.g. "1" for the first build of this
                                #version of your software. Increment
                                #for later re-builds of the same
                                #version of your software.  Text with
                                #changelog information to be displayed
                                #in the package "Details" tab of the
                                #Maemo Application Manager
    changeloginformation = "Merged changes from EPage (proper changelog later)\nNew Icon by Strutten."
    # 0.7.2 : Seek bar now responds to clicks (rather than drags)\nFixed bug with wrong text showing on button after changed chapter.
    # 0.7.1 : Fixed crash when current points to non existing book
    # 0.7.0 : Now ignores pressed outside the chapter selection menu\nAdded help
    # 0.6.1 : Fixed bug that prevented running on devices without Audiobook folder.
    #         Added tip on where to place audiobooks.
    # 0.6.0 : Now also plays .mp3 files
    # 0.5.0 : Second release. Now shows which chapter is playing, and scrolls to it when changing.
    # 0.4.9 : First release. Now it should work
    #  
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
        real_dir = root[len(dir_name):]
        if '.' in real_dir:
            continue # if some part of the dirname contains '.' we
                                        # ignore all files (avoid .svn
                                        # and others)
        fake_file = []
        for f in files:
            fake_file.append(root + os.sep + f + "|" + f)
        if len(fake_file) > 0:
            p[real_dir] = fake_file
    print p
    r = p.generate(version,build,changelog=changeloginformation,tar=True,dsc=True,changes=True,build=False,src=True)
