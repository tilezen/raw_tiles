from __future__ import absolute_import
from gzip import GzipFile
from io import BufferedWriter
import os


# gzip can do better if it has a lot of data to work with at once, so we
# buffer up a megabyte of data at a time. many tiles are larger than that,
# (uncompressed) so will benefit from being processed in fewer, bigger
# chunks.
BUFFER_SIZE = 1024 * 1024


class Gzip(object):

    # some small-scale experiments suggest that compression level 5 is the
    # best trade-off of tile size (relative to smallest size or time):
    #   level | size | time
    #     1   | 127% | 100%
    #     3   | 122% | 109%
    #     5   | 105% | 116%
    #     7   | 104% | 149%
    #     9   | 100% | 265%
    def __init__(self, formatter, compression_level=5):
        self.formatter = formatter
        self.compression_level = compression_level

    def create(self, io):
        gz = GzipFile(None, 'wb', self.compression_level, io)
        buf = BufferedWriter(gz, buffer_size=BUFFER_SIZE)
        return self.formatter.create(buf)

    def extension(self):
        return self.formatter.extension() + ".gz"
