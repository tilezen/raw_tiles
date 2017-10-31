from __future__ import absolute_import
from msgpack import Packer


class File(object):
    def __init__(self, io):
        self.io = io
        self.packer = Packer(use_bin_type=True)

    def write(self, *args):
        self.io.write(self.packer.pack(args))

    def flush(self):
        self.io.flush()

    def close(self):
        self.io.close()


class Msgpack(object):
    def create(self, io):
        return File(io)
