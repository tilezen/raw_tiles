from __future__ import absolute_import
import gzip
from msgpack import Unpacker
from collections import namedtuple, defaultdict
from raw_tiles.tile import Tile


def tile_contents(file_name):
    with gzip.open(file_name, 'rb') as gz:
        unpacker = Unpacker(file_like=gz)
        for obj in unpacker:
            yield obj


def deassoc(x):
    return dict((x[2*i], x[2*i+1]) for i in range(0, len(x)/2))


Route = namedtuple('Route', 'id tags')

class RouteIndex(object):

    def __init__(self):
        self.inverted = defaultdict(list)
        self.routes = dict()

    def add_relation(self, rel_id, way_off, rel_off, parts, members, tags):
        if tags is None:
            return

        way_ids = parts[way_off:rel_off]
        tags = deassoc(tags)

        if tags.get('type') == 'route':
            self.routes[rel_id] = Route(rel_id, tags)
            for way_id in way_ids:
                self.inverted[way_id].append(rel_id)

    def __call__(self, way_id):
        routes = []
        rel_ids = self.inverted.get(way_id)
        if rel_ids:
            routes = list()
            for rel_id in rel_ids:
                routes.append(self.routes[rel_id])

        return routes


def index(tile, *indices):
    file_name = 'tiles/osm/planet_osm_rels/%d/%d/%d.msgpack.gz' % \
        (tile.z, tile.x, tile.y)

    for obj in tile_contents(file_name):
        for index in indices:
            index.add_relation(*obj)


if __name__ == '__main__':
    import sys

    z, x, y = map(int, sys.argv[1].split("/"))
    tile = Tile(z, x, y)

    rt_idx = RouteIndex()
    index(tile, rt_idx)

    for way_id in map(int, sys.argv[2:]):
        routes = rt_idx(way_id)
        print ">>> WAY %d" % (way_id,)
        for route in routes:
            print "  %r" % (route,)
        print
