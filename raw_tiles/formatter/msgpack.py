from __future__ import absolute_import
from msgpack import Packer


class File(object):
    def __init__(self, io):
        self.io = io
        self.packer = Packer()

    def write(self, *args):
        self.io.write(self.packer.pack(args))

    def close(self):
        self.io.flush()
        self.io.close()


class Msgpack(object):
    def create(self, io):
        return File(io)

    def extension(self):
        return "msgpack"
