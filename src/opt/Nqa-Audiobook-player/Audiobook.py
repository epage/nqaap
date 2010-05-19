from __future__ import with_statement

import os

import logging


_moduleLogger = logging.getLogger(__name__)


class Audiobook(object):

    def __init__(self, path, current_chapter = 0):
        self.title = ""
        self._coverPath = ""
        self._chapterPaths = []
        self.current_chapter = current_chapter

        if is_playlist_book(path):
            self._scan_index(path)
        elif is_dir_book(path):
            self._scan_dir(path)
        elif is_single_chapter(path):
            self._scan_chapter(path)
        else:
            _moduleLogger.info("Audiobook not found in path: " + path)
            raise IOError("Audiobook directory not found")

        if len(self._chapterPaths) <= self.current_chapter:
            _moduleLogger.warning(
                "Audiobook chapter out of range (%s/%s)" % (
                    self.current_chapter, len(self._chapterPaths)
                )
            )
            self.current_chapter = 0

    @property
    def chapters(self):
        return self._chapterPaths

    def get_current_chapter(self):
        return self._chapterPaths[self.current_chapter]

    def set_chapter(self, chapter):
        if chapter in self.chapters:
            self.current_chapter = self.chapters.index(chapter)
        else:
            raise Exception("Unknown chapter set")

    def get_previous_chapter(self):
        """
        @returns the file name for the next chapter, without path
        """
        if 0 == self.current_chapter:
            return False
        else:
            self.current_chapter -= 1
            return self._chapterPaths[self.current_chapter]

    def get_next_chapter(self):
        """
        @returns the file name for the next chapter, without path
        """
        if len(self._chapterPaths) == self.current_chapter:
            return False
        else:
            self.current_chapter += 1
            return self._chapterPaths[self.current_chapter]

    def get_cover_img(self):
        if self._coverPath:
            return self._coverPath
        else:
            return "%s/NoCover.png" % os.path.dirname(__file__)

    def _scan_dir(self, root):
        self.title = os.path.split(root)[-1]
        dirContent = (
            os.path.join(root, f)
            for f in os.listdir(root)
            if not f.startswith(".")
        )

        files = [
            path
            for path in dirContent
            if os.path.isfile(os.path.join(root, path))
        ]

        images = [
            path
            for path in files
            if path.rsplit(".", 1)[-1] in ["png", "gif", "jpg", "jpeg"]
        ]
        if 0 < len(images):
            self._coverPath = images[0]

        self._chapterPaths = [
            path
            for path in files
            if is_single_chapter(path)
        ]
        self._chapterPaths.sort()

    def _scan_chapter(self, file):
        self._chapterPaths = [file]

    def _scan_playlist(self, file):
        root = os.path.dirname(file)
        self.title = os.path.basename(file).rsplit(".")[0]

        with open(file, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    continue
                path = line
                if not os.path.isabs(path):
                    path = os.path.normpath(os.path.join(root, path))
                self._chapterPaths.append(path)
        # Not sorting, assuming the file is in the desired order

    def _scan_index(self, file):
        import unicodedata

        # Reading file
        looking_for_title = False
        looking_for_cover = False
        looking_for_chapters = False

        with open(file, 'r') as f:
            for line in f:
                # title
                ascii = unicodedata.normalize('NFKD', unicode(line, "latin-1")).encode('ascii', 'ignore')
                print line[:-1], "PIC\n" in line, line in "#PIC"
                if "#BOOK" in line:
                    looking_for_title = True
                    continue
                if looking_for_title:
                    self.title = line[:-1]
                    looking_for_title = False
                if "#PIC" in line:
                    looking_for_cover = True
                    continue
                if looking_for_cover:
                    self.cover = line[:-1]
                    looking_for_cover = False
                if "#TRACKS" in line:
                    looking_for_chapters = True
                    continue
                if looking_for_chapters:
                    if "#CHAPTERS" in line:
                        break           # no further information needed
                    self.chapters.append(line.split(':')[0])


def is_dir_book(path):
    return os.path.isdir(path)


def is_playlist_book(path):
    return path.rsplit(".", 1)[-1] in ["m3u"]


def is_single_chapter(path):
    return path.rsplit(".", 1)[-1] in ["awb", "mp3", "spx", "ogg", "ac3", "wav"]


def is_book(path):
    if is_dir_book(path):
        return True
    elif is_playlist_book(path):
        return True
    elif is_single_chapter(path):
        return True
    else:
        return False
