from __future__ import absolute_import
import gzip
from msgpack import Unpacker
from raw_tiles.tile import Tile
from io import BufferedReader
from raw_tiles.index.features import FeatureTileIndex
from raw_tiles.index.highway import HighwayIndex
from raw_tiles.index.routes import RouteIndex


def tile_contents(tile, table):
    """
    Generator yielding each item in a gzipped msgpack format file.

    TODO: This should be generalised? Perhaps move into formatter classes?
    """

    file_name = 'tiles/osm/%s/%d/%d/%d.msgpack.gz' % \
        (table, tile.z, tile.x, tile.y)

    with BufferedReader(gzip.open(file_name, 'rb')) as gz:
        unpacker = Unpacker(file_like=gz)
        for obj in unpacker:
            yield obj


def index_table(source, *indices):
    """
    Index a table for the given tile coordinates. The function `add_row(...)`
    is called with each item (a.k.a row) in the tile for each of `*indices`.
    """

    for obj in source:
        for index in indices:
            index.add_row(*obj)


def index(get_table, indices):
    """
    Fill the given indices with data from all known tables for the given tile.
    Note that indices is expected to be a dict of table name mapping to a
    sequence of index objects callable with `add_row(...)`.
    """

    for typ in ('ways', 'rels', 'point', 'line', 'polygon'):
        table_name = 'planet_osm_' + typ
        table = get_table(table_name)
        table_indices = indices.get(table_name)
        if table_indices:
            index_table(table, *table_indices)


########################################################################
# NOTE: this is copied just to have a min zoom function to work with.
# later on, this will be importing the min zoom functions which
# tilequeue generates from the yaml, and so this copy-and-paste can be
# deleted.
#
# START COPY-PASTE
########################################################################
def calculate_1px_zoom(way_area):
    import math
    # can't take logarithm of zero, and some ways have
    # incredibly tiny areas, down to even zero. also, by z16
    # all features really should be visible, so we clamp the
    # computation at the way area which would result in 16
    # being returned.
    if way_area < 5.704:
        return 16
    else:
        return 17.256 - math.log(way_area) / math.log(4)


def landuse_min_zoom(fid, shape, props):
    if 'landuse' in props:
        return calculate_1px_zoom(shape.area)
    else:
        return None
########################################################################
# END COPY-PASTE
########################################################################

# simple test harness to build the indexes and then look up some ways,
# relations or tiles ("landuse" layer).
#
# for example, run as:
#
# $ python raw_tiles/command.py --dbparams dbname=california 10 163 395
# $ python raw_tiles/index/index.py 10/163/395 w225516713 w123741422 \
#      n298078639 t10/163/395 t15/5241/12668
#
# the first command generates a z10 tile over San Francisco. the second
# indexes that tile and looks up a couple of ways which are part of route
# relations, a node which is a gate and a couple of tiles containing
# various bits of landuse.
#
if __name__ == '__main__':
    import sys

    z, x, y = map(int, sys.argv[1].split("/"))
    tile = Tile(z, x, y)

    def get_table(table):
        return tile_contents(tile, table)

    rt_idx = RouteIndex()
    hw_idx = HighwayIndex()
    landuse_idx = FeatureTileIndex(tile, tile.z + 5, landuse_min_zoom)
    index(get_table, {
        'planet_osm_rels': [rt_idx],
        'planet_osm_ways': [hw_idx],
        'planet_osm_polygon': [landuse_idx],
    })

    for arg in sys.argv[2:]:
        typ = arg[0]

        if typ == 'n':
            elt_id = int(arg[1:])
            highways = hw_idx(elt_id)
            print ">>> NODE %d" % (elt_id,)
            for highway in highways:
                hw_type = highway.tags.get('highway')
                name = highway.tags.get('name')
                print "  %r\t%r" % (hw_type, name)
            print

        elif typ == 'w':
            elt_id = int(arg[1:])
            routes = rt_idx(elt_id)
            print ">>> WAY %d" % (elt_id,)
            for route in routes:
                rt_type = route.tags.get('route')
                name = route.tags.get('name')
                print "  %r\t%r" % (rt_type, name)
            print

        elif typ == 't':
            t = Tile(*map(int, arg[1:].split("/")))
            features = landuse_idx(t)
            print ">>> TILE %r" % (t,)
            for feature in features:
                fid = feature.id
                landuse = feature.properties.get('landuse')
                name = feature.properties.get('name')
                print "  %r\t%r\t%r" % (fid, landuse, name)
            print

        else:
            raise RuntimeError("Don't understand element type %r in "
                               "argument %r" % (typ, arg))
