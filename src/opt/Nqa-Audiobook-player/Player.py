import os
import threading
import time
import logging

import constants
import hildonize
import Audiobook
import FileStorage


_moduleLogger = logging.getLogger(__name__)


class Player(object):

    def __init__(self, ui):
        self.storage = FileStorage.FileStorage(path = constants._data_path_)
        if hildonize.IS_HILDON_SUPPORTED and not hildonize.IS_FREMANTLE_SUPPORTED:
            import SimpleOSSOPlayer as _SimplePlayer
            SimpleGStreamer = _SimplePlayer # silence PyFlakes
        else:
            import SimpleGStreamer as SimplePlayer
        self.player = SimplePlayer.SimplePlayer(self.next_chapter)
        self.ui = ui
        self.audiobook = None
        self._bookDir = None
        self._bookPaths = {}

    def get_books_path(self):
        return self._bookDir

    def load_books_path(self, booksPath):
        _moduleLogger.info("Loading books %s" % booksPath)
        if self.audiobook is not None:
            position = self.player.elapsed()
            self.storage.set_time(self.audiobook.current_chapter, position)

        self._bookDir = booksPath

        self._bookPaths = dict(
            (self.__format_name(bookPath), bookPath)
            for bookPath in self._find_books()
        )
        if self.ui is not None:
            bookPaths = self._bookPaths.values()
            bookPaths.sort()
            self.ui.set_books(bookPaths)

        lastBookName = self.storage.get_selected()
        if lastBookName is not None:
            _moduleLogger.info("continuing book: %s" % lastBookName)
            try:
                bookPath = self._bookPaths[lastBookName]
                self.set_book(bookPath)
            except KeyError:
                _moduleLogger.info("Audiobook was not found")
            except IOError:
                _moduleLogger.info("Audiobook could not be loaded")

    @staticmethod
    def __format_name(path):
        if os.path.isfile(path):
            return os.path.basename(path).rsplit(".", 1)[0]
        else:
            return os.path.basename(path)

    def set_book(self, bookPath):
        oldBookName = self.storage.get_selected()
        try:
            bookName = self.__format_name(bookPath)
            self.storage.select_book(bookName)
            chapter_num, _ = self.storage.get_time()
            self.audiobook = Audiobook.Audiobook(
                bookPath,
                chapter_num
            )
        except:
            self.storage.select_book(oldBookName)
            raise

        # self.player.set_file(self.audiobook.get_current_chapter())
        # self.player.seek_time(time) 

        if self.ui is not None:
            self.ui.set_book(bookPath, self.audiobook.get_cover_img())
            self.ui.set_chapters(self.audiobook.chapters)

        chapter_title = self.audiobook.chapters[chapter_num]
        self.set_chapter(chapter_title, True)

    def set_chapter(self, chapter, continuing = False):
        _moduleLogger.info("set chapter:" + chapter + " : Continuing: " + str(continuing))
        self.audiobook.set_chapter(chapter)
        self.player.set_file(self.audiobook.get_current_chapter())
        if not continuing:
            self.storage.set_time(self.audiobook.current_chapter, 0)

        if self.ui is not None:
            self.ui.set_chapter(self.audiobook.current_chapter)

    def previous_chapter(self, *args):
        _moduleLogger.info("Going back a chapter")
        self.player.stop()
        next_file = self.audiobook.get_previous_chapter()
        if next_file is not False:
            self.set_chapter(next_file)
            self.player.play()
        else:                           # the book is over
            self.storage.set_time(0, 0)

    def next_chapter(self, *args):
        _moduleLogger.info("Advancing a chapter")
        self.player.stop()
        next_file = self.audiobook.get_next_chapter()
        if next_file is not False:
            self.set_chapter(next_file)
            self.player.play()
        else:                           # the book is over
            self.storage.set_time(0, 0)

    def play(self):
        if self.audiobook is not None:
            self.player.play()
            _, target_time = self.storage.get_time()
            if 0 < target_time:
                time.sleep(1)
                self.player.seek_time(target_time)
            #print self.player.elapsed()
        else:
            print "No book selected, find one in ", self._bookDir

    def stop(self):
        position = self.player.elapsed()
        self.player.stop()

        if self.audiobook is not None:
            self.storage.set_time(self.audiobook.current_chapter, position)

    def is_playing(self):
        return self.player.playing

    def sleeptimer(self, secs):
        #print "sleeper", secs
        time.sleep(secs)
        #print "now its time to sleep"
        self.stop()

    def start_sleeptimer(self, secs):
        #print "startin sleep"
        sleep_thread = threading.Thread(target=self.sleeptimer, args=(secs, ))
        sleep_thread.start()
        #print "started sleep"

    def get_percentage(self):
        try:
            return float(self.player.elapsed()) / float(self.player.duration())
        except ZeroDivisionError:
            return 0.0

    def seek_percent(self, ratio):
        try:
            target = int(self.player.duration() * ratio) # Calculate where to seek
            self.player.seek_time(target)      # seek

            position = self.player.elapsed()
            self.storage.set_time(self.audiobook.current_chapter, target) # save position
            return True
        except:
            _moduleLogger.exception("Seek failed")
            return False

    def _find_books(self):
        try:
            paths = (
                os.path.join(self._bookDir, f)
                for f in os.listdir(self._bookDir)
            )
            return (
                path
                for path in paths
                if Audiobook.is_book(path)
            )
        except OSError:
            return ()
