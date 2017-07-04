from __future__ import absolute_import
from gzip import GzipFile


class Gzip(object):

    def __init__(self, formatter):
        self.formatter = formatter

    def create(self, io):
        gz = GzipFile(None, 'wb', 9, io)
        return self.formatter.create(gz)

    def extension(self):
        return self.formatter.extension() + ".gz"
