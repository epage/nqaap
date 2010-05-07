import os
import logging

import gst

import gtk_toolbox


_moduleLogger = logging.getLogger(__name__)


class SimplePlayer(object):

    def __init__(self, on_playing_done = None):
        #Fields
        self.playing = False
        self.__filename = ""
        self.__elapsed = 0
        self.__duration = 0

        #Event callbacks
        self.on_playing_done = on_playing_done

        #Set up GStreamer
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        #Constants
        self.time_format = gst.Format(gst.FORMAT_TIME)
        self.seek_flag = gst.SEEK_FLAG_FLUSH

    @property
    def has_file(self):
        return 0 < len(self.__filename)

    @gtk_toolbox.log_exception(_moduleLogger)
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:        # End-Of-Stream
            self.player.set_state(gst.STATE_NULL)
            self.playing = False
            if self.on_playing_done is not None: # event callback
                self.on_playing_done(self)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            #print "Error: %s" % err, debug
            _moduleLogger.error("Error: %s, (%s)" % (err, debug))
            self.playing = False

    def set_file(self, file):
        _moduleLogger.info("set file: %s", file)
        if os.path.isfile(file):
            if self.__filename != file:
                self._invalidate_cache()
            if self.playing:
                self.stop()

            file = os.path.abspath(file) # ensure absolute path
            _moduleLogger.debug("set file (absolute path): %s "%file)
            self.player.set_property("uri", "file://" + file)
            self.__filename = file
        else:
            _moduleLogger.error("File: %s not found" % file)

    def play(self):
        _moduleLogger.info("Started playing")
        self.player.set_state(gst.STATE_PLAYING)
        self.playing = True

    def stop(self):
        self.player.set_state(gst.STATE_NULL)
        self.playing = False
        _moduleLogger.info("Stopped playing")

    def elapsed(self):
        try:
            self.__elapsed = self.player.query_position(self.time_format, None)[0]
        except:
            pass
        return self.__elapsed

    def duration(self):
        try:
            self.__duration = self.player.query_duration(self.time_format, None)[0]
        except:
            _moduleLogger.exception("Query failed")
            pass
        return self.__duration

    def seek_time(self, ns):
        _moduleLogger.debug("Seeking to: %s", ns)
        self.player.seek_simple(self.time_format, self.seek_flag, ns)

    def _invalidate_cache(self):
        self.__elapsed = 0
        self.__duration = 0

    def __seek_percent(self, percent):
        format = gst.Format(gst.FORMAT_PERCENT)
        self.player.seek_simple(format, self.seek_flag, percent)
