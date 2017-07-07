from __future__ import absolute_import
from collections import namedtuple, defaultdict
from raw_tiles.index.util import deassoc


Highway = namedtuple('Highway', 'id tags')


class HighwayIndex(object):
    """
    Indexes the node members of highway ways, so that the highways using a
    given node ID can be looked up quickly.

    This is used in the min zoom calculation functions to assign a lower min
    zoom to gates which are on more major road types.
    """

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
