from __future__ import with_statement   # enable with

import os

import logging


log = logging.getLogger(__name__)


class FileStorage(object):

    def __init__(self, path="~/.SornPlayer/"):
        # Setup dir
        log.info("init filestorage")
        self.path = path
        self.books_path = os.path.join(self.path, "books/")
        if not os.path.isdir(self.books_path):
            os.makedirs(self.books_path)

        # Read config file
        self.conf = os.path.join(self.path, "current")
        self.selected = None

        if os.path.isfile(self.conf):
            with open(self.conf) as f:
                self.selected = f.readline()

        # Read current book file

    def get_selected(self):
        """returns the currently selected book"""
        return self.selected

    def select_book(self, bookName):
        """ Sets the book as the currently playing, and adds it to the
        database if it is not already there"""
        book_file = os.path.join(self.books_path, bookName)
        if not os.path.isfile(book_file):
            with open(book_file, 'w') as f:
                f.write("0\n") #Current chapter
                f.write("0\n") #Current position

        self.selected = bookName
        with open(self.conf, 'w') as f:
            f.write(self.selected) #

    def set_time(self, chapter, position):
        """ Sets the current time for the book that is currently selected"""
        try:
            book_file = os.path.join(self.books_path, self.selected)
            log.debug("writing time (%s, %s) to: %s"%( chapter, position, book_file ))
            with open(book_file, 'w') as f:
                f.write(str(int(chapter)) + "\n") #Current chapter
                f.write(str(int(position)) + "\n") #Current position
        except:
            log.error("Unable to save to file: %s" % book_file)

    def get_time(self):
        """Returns the current saved time for the current selected book"""
        chapter, position = 0 , 0
        book_file = os.path.join(self.books_path, self.selected)
        log.debug("getting time from: " + book_file)
        with open(book_file, 'r') as f:
            chapter = int(f.readline())
            position = int(f.readline())

        return chapter, position
