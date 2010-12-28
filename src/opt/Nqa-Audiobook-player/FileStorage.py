from __future__ import with_statement   # enable with

import os
import simplejson
import logging


_moduleLogger = logging.getLogger(__name__)


# @todo Add bookmarks


class FileStorage(object):

	def __init__(self, path="~/.SornPlayer/"):
		# Setup dir
		_moduleLogger.info("init filestorage")
		self.path = path
		self.books_path = os.path.join(self.path, "books.json")
		self.selected = None
		self._books = {}

	def load(self):
		if not os.path.isdir(self.path):
			os.makedirs(self.path)

		try:
			with open(self.books_path, "r") as settingsFile:
				settings = simplejson.load(settingsFile)
		except IOError, e:
			_moduleLogger.info("No settings")
			settings = {}
		except ValueError:
			_moduleLogger.info("Settings were corrupt")
			settings = {}

		if settings:
			self._books = settings["books"]
			self.selected = settings["selected"]
		else:
			_moduleLogger.info("Falling back to old settings format")
			self._load_old_settings()

	def save(self):
		settings = {
			"selected": self.selected,
			"books": self._books,
		}
		with open(self.books_path, "w") as settingsFile:
			simplejson.dump(settings, settingsFile)

	def get_selected(self):
		"""returns the currently selected book"""
		return self.selected

	def select_book(self, bookName):
		""" Sets the book as the currently playing, and adds it to the
		database if it is not already there"""
		book_file = os.path.join(self.books_path, bookName)
		if bookName not in self._books:
			self._books[bookName] = {
				"chapter": 0,
				"position": 0,
			}

		self.selected = bookName

	def set_time(self, chapter, position):
		""" Sets the current time for the book that is currently selected"""
		bookInfo = self._books[self.selected]
		bookInfo["chapter"] = chapter
		bookInfo["position"] = position

	def get_time(self):
		"""Returns the current saved time for the current selected book"""
		bookInfo = self._books[self.selected]
		return bookInfo["chapter"], bookInfo["position"]

	def _load_old_settings(self):
		conf = os.path.join(self.path, "current")

		try:
			with open(conf) as f:
				self.selected = f.readline()

			books_path = os.path.join(self.path, "books/")
			for book in os.listdir(books_path):
				book_file = os.path.join(books_path, book)
				with open(book_file, 'r') as f:
					chapter = int(f.readline())
					position = int(f.readline())
				self._books[book] = {
					"chapter": chapter,
					"position": position,
				}
		except IOError, e:
			if e.errno == 2:
				pass
			else:
				raise
		except OSError, e:
			if e.errno == 2:
				pass
			else:
				raise
