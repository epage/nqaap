#! /usr/bin/env python  

import logging

import dbus
import dbus.mainloop.glib
import gobject
import gtk

from Player import Player
from Gui import Gui


_moduleLogger = logging.getLogger(__name__)


def run():
    l = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    gobject.threads_init()
    gtk.gdk.threads_init()

    gui = Gui()
    controller = Player(ui = gui)
    gui.controller = controller
    gui.load_settings()

    gtk.main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
