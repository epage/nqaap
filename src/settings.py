#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of Multilist.

Multilist is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Multilist is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Multilist.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2008 Christoph Würstle
"""

import logging

import gtk

import hildonize
import gtk_toolbox

try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger(__name__)


class SettingsDialog(object):

	def __init__(self, parent):
		self.window = None

		self.__isPortraitCheckbutton = gtk.CheckButton("Portrait Mode")

		self.__rotationSection = gtk.VBox()
		self.__rotationSection.pack_start(self.__isPortraitCheckbutton, False, True)

		rotationFrame = gtk.Frame("Rotation")
		rotationFrame.add(self.__rotationSection)

		self.__audioBooksPath = gtk.Entry()
		self.__audioBooksPathButton = gtk.Button("Choose")
		self.__audioBooksPathButton.connect("clicked", self._on_path_choose)

		self.__audiobookPathSection = gtk.HBox()
		self.__audiobookPathSection.pack_start(self.__audioBooksPath, True, True)
		self.__audiobookPathSection.pack_start(self.__audioBooksPathButton, False, True)

		self.__audiobookSection = gtk.VBox()
		self.__audiobookSection.pack_start(self.__audiobookPathSection)

		audiobookFrame = gtk.Frame("Audiobooks")
		audiobookFrame.add(self.__audiobookSection)

		settingsBox = gtk.VBox()
		settingsBox.pack_start(rotationFrame, False, True)
		settingsBox.pack_start(audiobookFrame, False, True)
		settingsView = gtk.Viewport()
		settingsView.add(settingsBox)
		settingsScrollView = gtk.ScrolledWindow()
		settingsScrollView.add(settingsView)
		settingsScrollView.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		parent.pack_start(settingsScrollView, True, True)

		settingsScrollView = hildonize.hildonize_scrollwindow(settingsScrollView)

	def set_portrait_state(self, isPortrait):
		self.__isPortraitCheckbutton.set_active(isPortrait)

	def is_portrait(self):
		return self.__isPortraitCheckbutton.get_active()

	def set_audiobook_path(self, path):
		self.__audioBooksPath.set_text(path)

	def get_audiobook_path(self):
		return self.__audioBooksPath.get_text()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_path_choose(self, *args):
		fileChooser = gtk.FileChooserDialog(
			title="Audiobooks",
			action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			parent=self.window,
		)
		fileChooser.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		fileChooser.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		fileChooser.set_filename(self.__audioBooksPath.get_text())
		userResponse = fileChooser.run()
		fileChooser.hide()
		if userResponse == gtk.RESPONSE_OK:
			filename = fileChooser.get_filename()
			self.__audioBooksPath.set_text(filename)
