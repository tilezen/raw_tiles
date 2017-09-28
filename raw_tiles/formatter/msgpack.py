from __future__ import absolute_import
from msgpack import Packer


class File(object):
    def __init__(self, io):
        self.io = io
        self.packer = Packer(use_bin_type=True)

    def write(self, *args):
        args = tuple(bytes(x) if isinstance(x, buffer) else x
                     for x in args)
        self.io.write(self.packer.pack(args))

    def close(self):
        self.io.flush()
        self.io.close()


class Msgpack(object):
    def create(self, io):
        return File(io)

    def extension(self):
        return "msgpack"
