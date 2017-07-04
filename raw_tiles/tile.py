from collections import namedtuple
from raw_tiles.util import st_box2d_for_tile

class Tile(namedtuple("Tile", "z x y")):
    def box2d(self):
        return st_box2d_for_tile(self.z, self.x, self.y)
