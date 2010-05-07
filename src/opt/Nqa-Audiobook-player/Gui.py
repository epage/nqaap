from __future__ import with_statement

import os
import ConfigParser
import logging

import gobject
import gtk

import constants
import hildonize
import gtk_toolbox
import Browser
import CallMonitor
import settings

if hildonize.IS_FREMANTLE_SUPPORTED:
    # I don't normally do this but I want to error as loudly as possibly when an issue arises
    import hildon


_moduleLogger = logging.getLogger(__name__)


class Gui(object):

    def __init__(self):
        _moduleLogger.info("Starting GUI")
        self._clipboard = gtk.clipboard_get()
        self._callMonitor = CallMonitor.CallMonitor()
        self.__settingsWindow = None
        self.__settingsManager = None
        self._bookSelection = []
        self._bookSelectionIndex = -1
        self._chapterSelection = []
        self._chapterSelectionIndex = -1
        self._sleepSelection = ["0", "1", "10", "20", "30", "60"]
        self._sleepSelectionIndex = 0

        self.__window_in_fullscreen = False #The window isn't in full screen mode initially.
        self.__isPortrait = False

        self.controller = None
        self.sleep_timer = None
        self.auto_chapter_selected = False # true if we are in the
                                           # midle of an automatic
                                           # chapter change

        self.ignore_next_chapter_change = False
        # set up gui
        self.setup()
        self._callMonitor.connect("call_start", self.__on_call_started)
        self._callMonitor.start()

    def setup(self):
        if hildonize.IS_FREMANTLE_SUPPORTED:
            gtk.set_application_name(constants.__pretty_app_name__) # window title
        self._app = hildonize.get_app_class()()
        self.win = gtk.Window()
        self.win = hildonize.hildonize_window(self._app, self.win)

        # Cover image
        self.cover = gtk.Image()

        # Controls:

        # Label that hold the title of the book,and maybe the chapter
        self.title = gtk.Label("Select a book to start listening")
        self.title.set_justify(gtk.JUSTIFY_CENTER)

        # Seekbar 
        if hildonize.IS_FREMANTLE_SUPPORTED:
            self.seek = hildon.Seekbar()
            self.seek.set_range(0.0, 100)
            self.seek.set_draw_value(False)
            self.seek.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
            self.seek.connect('change-value', self.seek_changed) # event
            # self.seek.connect('value-changed',self.seek_changed) # event
        else:
            adjustment = gtk.Adjustment(0, 0, 101, 1, 5, 1)
            self.seek = gtk.HScale(adjustment)
            self.seek.connect('change-value', self.seek_changed) # event

        # Pause button
        if hildonize.IS_FREMANTLE_SUPPORTED:
            self.backButton = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            image = gtk.image_new_from_stock(gtk.STOCK_GO_BACK, gtk.HILDON_SIZE_FINGER_HEIGHT)
            self.backButton.set_image(image)

            self.button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)

            self.forwardButton = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            image = gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD, gtk.HILDON_SIZE_FINGER_HEIGHT)
            self.forwardButton.set_image(image)
        else:
            self.backButton = gtk.Button(stock=gtk.STOCK_GO_BACK)
            self.button = gtk.Button()
            self.forwardButton = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        self.set_button_text("Play", "Start playing the audiobook")
        self.backButton.connect('clicked', self._on_previous_chapter)
        self.button.connect('clicked', self.play_pressed) # event
        self.forwardButton.connect('clicked', self._on_next_chapter)

        self._toolbar = gtk.HBox()
        self._toolbar.pack_start(self.backButton, False, False, 0)
        self._toolbar.pack_start(self.button, True, True, 0)
        self._toolbar.pack_start(self.forwardButton, False, False, 0)

        # Box to hold the controls:
        self._controlLayout = gtk.VBox()
        self._controlLayout.pack_start(self.title, True, True, 0)
        self._controlLayout.pack_start(self.seek, True, True, 0)
        self._controlLayout.pack_start(self._toolbar, False, True, 0)

        #Box that divides the layout in two: cover on the lefta
        #and controls on the right
        self._viewLayout = gtk.HBox()
        self._viewLayout.pack_start(self.cover, True, True, 0)
        self._viewLayout.add(self._controlLayout)

        self._menuBar = gtk.MenuBar()
        self._menuBar.show()

        self._mainLayout = gtk.VBox()
        self._mainLayout.pack_start(self._menuBar, False, False, 0)
        self._mainLayout.pack_start(self._viewLayout)

        # Add hbox to the window
        self.win.add(self._mainLayout)

        #Menu:
        # Create menu
        self._populate_menu()

        self.win.connect("delete_event", self.quit) # Add shutdown event
        self.win.connect("key-press-event", self.on_key_press)
        self.win.connect("window-state-event", self._on_window_state_change)

        self.win.show_all()

        # Run update timer
        self.setup_timers()

    def _populate_menu(self):
        self._menuBar = hildonize.hildonize_menu(
            self.win,
            self._menuBar,
        )
        if hildonize.IS_FREMANTLE_SUPPORTED:
            # Create a picker button 
            self.book_button = hildon.Button(gtk.HILDON_SIZE_AUTO,
                                              hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self.book_button.set_title("Audiobook") # Set a title to the button 
            self.book_button.connect("clicked", self._on_select_audiobook)

            # Create a picker button 
            self.chapter_button = hildon.Button(gtk.HILDON_SIZE_AUTO,
                                              hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self.chapter_button.set_title("Chapter") # Set a title to the button 
            self.chapter_button.connect("clicked", self._on_select_chapter)

            # Create a picker button 
            self.sleeptime_button = hildon.Button(gtk.HILDON_SIZE_AUTO,
                                              hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self.sleeptime_button.set_title("Sleeptimer") # Set a title to the button 
            self.sleeptime_button.connect("clicked", self._on_select_sleep)

            settings_button = hildon.Button(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            settings_button.set_label("Settings")
            settings_button.connect("clicked", self._on_settings)

            help_button = hildon.Button(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            help_button.set_label("Help")
            help_button.connect("clicked", self.get_help)

            self._menuBar.append(self.book_button)        # Add the button to menu
            self._menuBar.append(self.chapter_button)        # Add the button to menu
            self._menuBar.append(self.sleeptime_button)        # Add the button to menu
            self._menuBar.append(settings_button)
            self._menuBar.append(help_button)
            self._menuBar.show_all()
        else:
            self._audiobookMenuItem = gtk.MenuItem("Audiobook: ")
            self._audiobookMenuItem.connect("activate", self._on_select_audiobook)

            self._chapterMenuItem = gtk.MenuItem("Chapter: ")
            self._chapterMenuItem.connect("activate", self._on_select_chapter)

            self._sleepMenuItem = gtk.MenuItem("Sleeptimer: 0")
            self._sleepMenuItem.connect("activate", self._on_select_sleep)

            settingsMenuItem = gtk.MenuItem("Settings")
            settingsMenuItem.connect("activate", self._on_settings)

            helpMenuItem = gtk.MenuItem("Help")
            helpMenuItem.connect("activate", self.get_help)

            booksMenu = gtk.Menu()
            booksMenu.append(self._audiobookMenuItem)
            booksMenu.append(self._chapterMenuItem)
            booksMenu.append(self._sleepMenuItem)
            booksMenu.append(settingsMenuItem)
            booksMenu.append(helpMenuItem)

            booksMenuItem = gtk.MenuItem("Books")
            booksMenuItem.show()
            booksMenuItem.set_submenu(booksMenu)
            self._menuBar.append(booksMenuItem)
            self._menuBar.show_all()

    def setup_timers(self):
        self.seek_timer = timeout_add_seconds(3, self.update_seek)

    def save_settings(self):
        config = ConfigParser.SafeConfigParser()
        self._save_settings(config)
        with open(constants._user_settings_, "wb") as configFile:
            config.write(configFile)

    def _save_settings(self, config):
        config.add_section(constants.__pretty_app_name__)
        config.set(constants.__pretty_app_name__, "portrait", str(self.__isPortrait))
        config.set(constants.__pretty_app_name__, "fullscreen", str(self.__window_in_fullscreen))
        config.set(constants.__pretty_app_name__, "audiopath", self.controller.get_books_path())

    def load_settings(self):
        config = ConfigParser.SafeConfigParser()
        config.read(constants._user_settings_)
        self._load_settings(config)

    def _load_settings(self, config):
        isPortrait = False
        window_in_fullscreen = False
        booksPath = constants._default_book_path_
        try:
            isPortrait = config.getboolean(constants.__pretty_app_name__, "portrait")
            window_in_fullscreen = config.getboolean(constants.__pretty_app_name__, "fullscreen")
            booksPath = config.get(constants.__pretty_app_name__, "audiopath")
        except ConfigParser.NoSectionError, e:
            _moduleLogger.info(
                "Settings file %s is missing section %s" % (
                    constants._user_settings_,
                    e.section,
                )
            )

        if isPortrait ^ self.__isPortrait:
            if isPortrait:
                orientation = gtk.ORIENTATION_VERTICAL
            else:
                orientation = gtk.ORIENTATION_HORIZONTAL
            self.set_orientation(orientation)

        self.__window_in_fullscreen = window_in_fullscreen
        if self.__window_in_fullscreen:
            self.win.fullscreen()
        else:
            self.win.unfullscreen()

        self.controller.load_books_path(booksPath)

    @staticmethod
    def __format_name(path):
        if os.path.isfile(path):
            return os.path.basename(path).rsplit(".", 1)[0]
        else:
            return os.path.basename(path)

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_select_audiobook(self, *args):
        if not self._bookSelection:
            return
        index = hildonize.touch_selector(
            self.win,
            "Audiobook",
            (self.__format_name(bookPath) for bookPath in self._bookSelection),
            self._bookSelectionIndex if 0 <= self._bookSelectionIndex else 0,
        )
        self._bookSelectionIndex = index
        bookName = self._bookSelection[index]
        self.controller.set_book(bookName)

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_select_chapter(self, *args):
        if not self._chapterSelection:
            return
        index = hildonize.touch_selector(
            self.win,
            "Chapter",
            (self.__format_name(chapterPath) for chapterPath in self._chapterSelection),
            self._chapterSelectionIndex if 0 <= self._chapterSelectionIndex else 0,
        )
        self._chapterSelectionIndex = index
        chapterName = self._chapterSelection[index]
        self.controller.set_chapter(chapterName)

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_select_sleep(self, *args):
        if self.sleep_timer is not None:
            gobject.source_remove(self.sleep_timer)

        try:
            index = hildonize.touch_selector(
                self.win,
                "Sleeptimer",
                self._sleepSelection,
                self._sleepSelectionIndex if 0 <= self._sleepSelectionIndex else 0,
            )
        except RuntimeError:
            _moduleLogger.exception("Handling as if user cancelled")
            hildonize.show_information_banner(self.win, "Sleep timer canceled")
            index = 0

        self._sleepSelectionIndex = index
        sleepName = self._sleepSelection[index]

        time_out = int(sleepName)
        if 0 < time_out:
            timeout_add_seconds(time_out * 60, self.sleep)

        if hildonize.IS_FREMANTLE_SUPPORTED:
            self.sleeptime_button.set_text("Sleeptimer", sleepName)
        else:
            self._sleepMenuItem.get_child().set_text("Sleeptimer: %s" % (sleepName, ))

    @gtk_toolbox.log_exception(_moduleLogger)
    def __on_call_started(self, callMonitor):
        self.pause()

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_settings(self, *args):
        if self.__settingsWindow is None:
            vbox = gtk.VBox()
            self.__settingsManager = settings.SettingsDialog(vbox)

            self.__settingsWindow = gtk.Window()
            self.__settingsWindow.add(vbox)
            self.__settingsWindow = hildonize.hildonize_window(self._app, self.__settingsWindow)
            self.__settingsManager.window = self.__settingsWindow

            self.__settingsWindow.set_title("Settings")
            self.__settingsWindow.set_transient_for(self.win)
            self.__settingsWindow.set_default_size(*self.win.get_size())
            self.__settingsWindow.connect("delete-event", self._on_settings_delete)
        self.__settingsManager.set_portrait_state(self.__isPortrait)
        self.__settingsManager.set_audiobook_path(self.controller.get_books_path())
        self.__settingsWindow.set_modal(True)
        self.__settingsWindow.show_all()

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_settings_delete(self, *args):
        self.__settingsWindow.emit_stop_by_name("delete-event")
        self.__settingsWindow.hide()
        self.__settingsWindow.set_modal(False)

        isPortrait = self.__settingsManager.is_portrait()
        if isPortrait ^ self.__isPortrait:
            if isPortrait:
                orientation = gtk.ORIENTATION_VERTICAL
            else:
                orientation = gtk.ORIENTATION_HORIZONTAL
            self.set_orientation(orientation)
        if self.__settingsManager.get_audiobook_path() != self.controller.get_books_path():
            self.controller.load_books_path(self.__settingsManager.get_audiobook_path())

        return True

    @gtk_toolbox.log_exception(_moduleLogger)
    def update_seek(self):
        #print self.controller.get_percentage()
        if self.controller.is_playing():
            gtk.gdk.threads_enter()
            self.seek.set_value(self.controller.get_percentage() * 100)
            gtk.gdk.threads_leave()
        #self.controller.get_percentage() 
        return True                     # run again

    @gtk_toolbox.log_exception(_moduleLogger)
    def sleep(self):
        _moduleLogger.info("sleep time timeout")
        hildonize.show_information_banner(self.win, "Sleep timer")
        self.controller.stop()
        self.set_button_text("Resume", "Resume playing the audiobook")
        return False                    # do not repeat

    @gtk_toolbox.log_exception(_moduleLogger)
    def get_help(self, button):
        Browser.open("file:///opt/Nqa-Audiobook-player/Help/nqaap.html")

    @gtk_toolbox.log_exception(_moduleLogger)
    def seek_changed(self, seek, scroll , value):
        # print "sok", scroll
        self.controller.seek_percent(seek.get_value() / 100.0)

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_next_chapter(self, *args):
        self.controller.next_chapter()

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_previous_chapter(self, *args):
        self.controller.previous_chapter()

    @gtk_toolbox.log_exception(_moduleLogger)
    def play_pressed(self, button):
        if self.controller.is_playing():
            self.pause()
        else:
            self.play()

    @gtk_toolbox.log_exception(_moduleLogger)
    def on_key_press(self, widget, event, *args):
        RETURN_TYPES = (gtk.keysyms.Return, gtk.keysyms.ISO_Enter, gtk.keysyms.KP_Enter)
        isCtrl = bool(event.get_state() & gtk.gdk.CONTROL_MASK)
        if (
            event.keyval == gtk.keysyms.F6 or
            event.keyval in RETURN_TYPES and isCtrl
        ):
            # The "Full screen" hardware key has been pressed 
            if self.__window_in_fullscreen:
                self.win.unfullscreen ()
            else:
                self.win.fullscreen ()
            return True
        elif event.keyval == gtk.keysyms.o and isCtrl:
            self._toggle_rotate()
            return True
        elif (
            event.keyval in (gtk.keysyms.w, gtk.keysyms.q) and
            event.get_state() & gtk.gdk.CONTROL_MASK
        ):
            self.quit()
        elif event.keyval == gtk.keysyms.l and event.get_state() & gtk.gdk.CONTROL_MASK:
            with open(constants._user_logpath_, "r") as f:
                logLines = f.xreadlines()
                log = "".join(logLines)
                self._clipboard.set_text(str(log))
            return True
        elif event.keyval in RETURN_TYPES:
            if self.controller.is_playing():
                self.pause()
            else:
                self.play()
            return True
        elif event.keyval == gtk.keysyms.Left:
            self.controller.previous_chapter()
            return True
        elif event.keyval == gtk.keysyms.Right:
            self.controller.next_chapter()
            return True

    @gtk_toolbox.log_exception(_moduleLogger)
    def _on_window_state_change(self, widget, event, *args):
        if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.__window_in_fullscreen = True
        else:
            self.__window_in_fullscreen = False

    @gtk_toolbox.log_exception(_moduleLogger)
    def quit(self, *args):             # what are the arguments?
        _moduleLogger.info("Shutting down")
        try:
            self.save_settings()
            self.controller.stop()          # to save the state
        finally:
            gtk.main_quit()

    # Actions:  

    def play(self):
        self.set_button_text("Stop", "Stop playing the audiobook")
        self.controller.play()

    def pause(self):
        self.set_button_text("Resume", "Resume playing the audiobook")
        self.controller.stop()

    def set_orientation(self, orientation):
        if orientation == gtk.ORIENTATION_VERTICAL:
            if self.__isPortrait:
                return
            hildonize.window_to_portrait(self.win)
            self.__isPortrait = True

            self._viewLayout.remove(self._controlLayout)
            self._mainLayout.add(self._controlLayout)
        elif orientation == gtk.ORIENTATION_HORIZONTAL:
            if not self.__isPortrait:
                return
            hildonize.window_to_landscape(self.win)
            self.__isPortrait = False

            self._mainLayout.remove(self._controlLayout)
            self._viewLayout.add(self._controlLayout)
        else:
            raise NotImplementedError(orientation)

    def get_orientation(self):
        return gtk.ORIENTATION_VERTICAL if self.__isPortrait else gtk.ORIENTATION_HORIZONTAL

    def _toggle_rotate(self):
        if self.__isPortrait:
            self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        else:
            self.set_orientation(gtk.ORIENTATION_VERTICAL)

    def change_chapter(self, chapterName):
        if chapterName is None:
            _moduleLogger.debug("chapter selection canceled.")
            #import pdb; pdb.set_trace()     # start debugger
            self.ignore_next_chapter_change = True
            return True                   # this should end the function and indicate it has been handled

        if self.ignore_next_chapter_change:
            self.ignore_next_chapter_change = False
            _moduleLogger.debug("followup chapter selection canceled.")
            #import pdb; pdb.set_trace()     # start debugger
            return True                   # this should end the function and indicate it has been handled

        if self.auto_chapter_selected:
            _moduleLogger.debug("chapter changed (by controller) to: %s" % chapterName)
            self.auto_chapter_selected = False
            # do nothing
        else:
            _moduleLogger.debug("chapter selection sendt to controller: %s" % chapterName)
            self.controller.set_chapter(chapterName) # signal controller
            self.set_button_text("Play", "Start playing the audiobook") # reset button

    def set_button_text(self, title, text):
        if hildonize.IS_FREMANTLE_SUPPORTED:
            self.button.set_text(title, text)
        else:
            self.button.set_label("%s - %s" % (title, text))

    def set_books(self, books):
        _moduleLogger.debug("new books")
        del self._bookSelection[:]
        self._bookSelection.extend(books)
        if len(books) == 0 and self.controller is not None:
            hildonize.show_information_banner(self.win, "No audiobooks found. \nPlease place your audiobooks in the directory %s" % self.controller.get_books_path())

    def set_book(self, bookPath, cover):
        bookName = self.__format_name(bookPath)

        self.set_button_text("Play", "Start playing the audiobook") # reset button
        self.title.set_text(bookName)
        if hildonize.IS_FREMANTLE_SUPPORTED:
            self.book_button.set_text("Audiobook", bookName)
        else:
            self._audiobookMenuItem.get_child().set_text("Audiobook: %s" % (bookName, ))
        if cover != "":
            self.cover.set_from_file(cover)

    def set_chapter(self, chapterIndex):
        '''
        Called from controller whenever a new chapter is started

        chapter parameter is supposed to be the index for the chapter, not the name
        '''
        self.auto_chapter_selected = True
        if hildonize.IS_FREMANTLE_SUPPORTED:
            self.chapter_button.set_text("Chapter", str(chapterIndex))
        else:
            self._chapterMenuItem.get_child().set_text("Chapter: %s" % (chapterIndex, ))

    def set_chapters(self, chapters):
        _moduleLogger.debug("setting chapters" )
        del self._chapterSelection[:]
        self._chapterSelection.extend(chapters)

    def set_sleep_timer(self, mins):
        pass

    # Utils
    def set_selected_value(self, button, value):
        i = button.get_selector().get_model(0).index[value] # get index of value from list
        button.set_active(i)                                # set active index to that index


def _old_timeout_add_seconds(timeout, callback):
    return gobject.timeout_add(timeout * 1000, callback)


def _timeout_add_seconds(timeout, callback):
    return gobject.timeout_add_seconds(timeout, callback)


try:
    gobject.timeout_add_seconds
    timeout_add_seconds = _timeout_add_seconds
except AttributeError:
    timeout_add_seconds = _old_timeout_add_seconds


if __name__ == "__main__":
    g = Gui(None)
