from shapely import wkb
from msgpack import Packer, Unpacker
from contextlib import contextmanager


class Writer:
    def __init__(self, io):
        self.io = io
        self.packer = Packer()

    def write(self, fid, wkb, props):
        self.io.write(self.packer.pack([fid, bytes(wkb), props]))

    def close(self):
        pass


@contextmanager
def write(io):
    w = Writer(io)
    yield w
    w.close()


def read(io):
    unpacker = Unpacker(file_like=io)
    for fid, wkb_data, props in unpacker:
        geom = wkb.loads(wkb_data)
        yield (fid, geom, props)
