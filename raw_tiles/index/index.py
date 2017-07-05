from __future__ import absolute_import
import gzip
from msgpack import Unpacker
from collections import namedtuple, defaultdict
from raw_tiles.tile import Tile
from io import BufferedReader
from itertools import izip


def tile_contents(file_name):
    with BufferedReader(gzip.open(file_name, 'rb')) as gz:
        unpacker = Unpacker(file_like=gz)
        for obj in unpacker:
            yield obj


def deassoc(x):
    pairs = [iter(x)] * 2
    return dict(izip(*pairs))


Route = namedtuple('Route', 'id tags')


class RouteIndex(object):

    def __init__(self):
        self.inverted = defaultdict(list)
        self.routes = dict()

    def add_relation(self, rel_id, way_off, rel_off, parts, members, tags):
        if tags is None:
            return

        # early return if the tags associative array doesn't contain 'route'.
        # it turns out that converting this into a dict takes a significant
        # amount of time, so it's better to avoid it where possible.
        if 'route' not in tags:
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


Highway = namedtuple('Highway', 'id tags')


class HighwayIndex(object):

    def __init__(self):
        self.inverted = defaultdict(set)
        self.highways = dict()

    def add_way(self, way_id, nodes, tags):
        if tags is None:
            return

        # early return if the tags associative array doesn't contain
        # 'highway'. it turns out that converting this into a dict takes a
        # significant amount of time, so it's better to avoid it where
        # possible.
        if 'highway' not in tags:
            return

        tags = deassoc(tags)

        if tags.get('highway'):
            self.highways[way_id] = Highway(way_id, tags)
            for node_id in nodes:
                self.inverted[node_id].add(way_id)

    def __call__(self, node_id):
        highways = []
        way_ids = self.inverted.get(node_id)
        if way_ids:
            highways = list()
            for way_id in way_ids:
                highways.append(self.highways[way_id])

        return highways


def index_table(tile, table, index_fn, *indices):
    file_name = 'tiles/osm/%s/%d/%d/%d.msgpack.gz' % \
        (table, tile.z, tile.x, tile.y)

    # filter only indices which respond to index_fn
    indexable = list()
    for index in indices:
        if callable(getattr(index, index_fn, None)):
            indexable.append(index)

    if indexable:
        for obj in tile_contents(file_name):
            for index in indexable:
                getattr(index, index_fn)(*obj)


def index(tile, *indices):
    index_table(tile, 'planet_osm_ways', 'add_way', *indices)
    index_table(tile, 'planet_osm_rels', 'add_relation', *indices)


if __name__ == '__main__':
    import sys

    z, x, y = map(int, sys.argv[1].split("/"))
    tile = Tile(z, x, y)

    rt_idx = RouteIndex()
    hw_idx = HighwayIndex()
    index(tile, rt_idx, hw_idx)

    for arg in sys.argv[2:]:
        typ = arg[0]
        elt_id = int(arg[1:])

        if typ == 'n':
            highways = hw_idx(elt_id)
            print ">>> NODE %d" % (elt_id,)
            for highway in highways:
                hw_type = highway.tags.get('highway')
                name = highway.tags.get('name')
                print "  %r\t%r" % (hw_type, name)
            print

        elif typ == 'w':
            routes = rt_idx(elt_id)
            print ">>> WAY %d" % (elt_id,)
            for route in routes:
                rt_type = route.tags.get('route')
                name = route.tags.get('name')
                print "  %r\t%r" % (rt_type, name)
            print

        else:
            raise RuntimeError("Don't understand element type %r in "
                               "argument %r" % (typ, arg))
