from __future__ import absolute_import
from collections import namedtuple
from raw_tiles.util import st_box2d_for_tile, bbox_for_tile
from raw_tiles.util import MERCATOR_WORLD_SIZE
from shapely.geometry import box as make_box
from math import floor, ceil


class Tile(namedtuple("Tile", "z x y")):
    def box2d(self):
        return st_box2d_for_tile(self.z, self.x, self.y)

    def as_shapely(self):
        return make_box(*bbox_for_tile(self.z, self.x, self.y))

    def parent(self):
        if self.z == 0:
            return None

        return Tile(self.z - 1, int(self.x / 2), int(self.y / 2))


def _floor(x):
    """
    Return the largest integer which is smaller than x. This is different from
    the usual math.floor method, which returns the largest integer smaller than
    or equal to x.

    This extra rounding down when x is already integral is used to make sure
    that the boundary of shapes are fully covered when they are exactly on a
    tile boundary.
    """

    f = floor(x)
    if x == f:
        f -= 1.0
    return int(f)


def _ceil(x):
    """
    Return the smallest integer which is greater than x. This is different from
    the usual math.ceil method, which returns the smallest integer which is
    greater than or equal to x.

    This extra rounding up when x is already integral is used to make sure
    that the boundary of shapes are fully covered when they are exactly on a
    tile boundary.
    """

    f = ceil(x)
    if x == f:
        f += 1.0
    return int(f)


def shape_tile_coverage(shape, zoom, root_tile):
    """
    Calculates the set of tiles that shape covers at the given zoom, and for
    the given root tile (i.e: all returned tiles will have the root tile in
    their hierarchy of parents. This prevents the coverage list from being
    extremely large for large input polygons.
    """

    assert root_tile.z <= zoom

    # if the geometry is empty, then it covers no tiles.
    if shape.is_empty:
        return set()

    minx, miny, maxx, maxy = shape.bounds
    max_coord = 2 ** zoom
    rx = int(root_tile.x)
    ry = int(root_tile.y)
    rz = int(root_tile.z)

    minx = _floor(max_coord * (0.5 + minx / MERCATOR_WORLD_SIZE))
    maxx = _ceil(max_coord * (0.5 + maxx / MERCATOR_WORLD_SIZE))
    maxy = _floor(max_coord * (0.5 - maxy / MERCATOR_WORLD_SIZE))
    miny = _ceil(max_coord * (0.5 - miny / MERCATOR_WORLD_SIZE))
    # swap min/max y, since we inverted the coordinate system
    miny, maxy = maxy, miny

    # clip to the root_tile
    zoom_diff = zoom - rz
    zoom_mult = 2 ** zoom_diff
    minx = max(minx, rx * zoom_mult)
    miny = max(miny, ry * zoom_mult)
    maxx = min(maxx, (rx + 1) * zoom_mult - 1)
    maxy = min(maxy, (ry + 1) * zoom_mult - 1)

    tiles = set()
    for x in range(minx, maxx + 1):
        for y in range(miny, maxy + 1):
            tile = Tile(zoom, x, y)
            if tile.as_shapely().intersects(shape):
                tiles.add(tile)

    return tiles
