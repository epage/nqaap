import os
import logging

import dbus

import gtk_toolbox


_moduleLogger = logging.getLogger(__name__)


class SimplePlayer(object):

	SERVICE_NAME		 = "com.nokia.osso_media_server"
	OBJECT_PATH		  = "/com/nokia/osso_media_server"
	AUDIO_INTERFACE_NAME = "com.nokia.osso_media_server.music"

	def __init__(self, on_playing_done = None):
		#Fields
		self.has_file = False
		self.playing = False
		self.__elapsed = 0

		#Event callbacks
		self.on_playing_done = on_playing_done

		session_bus = dbus.SessionBus()

		# Get the osso-media-player proxy object
		oms_object = session_bus.get_object(
			self.SERVICE_NAME,
			self.OBJECT_PATH,
			introspect=False,
			follow_name_owner_changes=True,
		)
		# Use the audio interface
		oms_audio_interface = dbus.Interface(
			oms_object,
			self.AUDIO_INTERFACE_NAME,
		)
		self._audioProxy = oms_audio_interface

		self._audioProxy.connect_to_signal("state_changed", self._on_state_changed)
		self._audioProxy.connect_to_signal("end_of_stream", self._on_end_of_stream)

		error_signals = [
			"no_media_selected",
			"file_not_found",
			"type_not_found",
			"unsupported_type",
			"gstreamer",
			"dsp",
			"device_unavailable",
			"corrupted_file",
			"out_of_memory",
			"audio_codec_not_supported",
		]
		for error in error_signals:
			self._audioProxy.connect_to_signal(error, self._on_error)

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_error(self, *args):
		self.playing = False

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_end_of_stream(self, *args):
		self.playing = False
		if self.on_playing_done is not None: # event callback
			self.on_playing_done(self)

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_state_changed(self, state):
		_moduleLogger.info("State: %s", state)

	def set_file(self, file):
		_moduleLogger.info("set file: %s", file)
		if os.path.isfile(file):
			if self.playing:
				self.stop()

			uri = "file://" + file
			self._audioProxy.set_media_location(uri)
			self.has_file = True
		else:
			_moduleLogger.error("File: %s not found" % file)

	def play(self):
		_moduleLogger.info("Started playing")
		self._audioProxy.play()
		self.playing = True

	def stop(self):
		self._audioProxy.stop()
		self.playing = False
		_moduleLogger.info("Stopped playing")

	def elapsed(self):
		pos_info = self._audioProxy.get_position()
		if isinstance(pos_info, tuple):
			pos, _ = pos_info
			return pos
		else:
			return 0

	def duration(self):
		pos_info = self._audioProxy.get_position()
		if isinstance(pos_info, tuple):
			_, dur = pos_info
			return dur
		else:
			return 0

	def seek_time(self, ns):
		_moduleLogger.debug("Seeking to: %s", ns)
		self._audioProxy.seek( dbus.Int32(1), dbus.Int32(ns) )
