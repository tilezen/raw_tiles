from __future__ import absolute_import
from collections import namedtuple, defaultdict
from raw_tiles.index.util import deassoc


Route = namedtuple('Route', 'id tags')


class RouteIndex(object):
    """
    Indexes the way members of type=route relations, allowing very fast lookup
    of the routes for a given way ID.

    This will be used by the min zoom and kind calculation functions, as we
    bump roads up a few zoom levels when they're part of major routes.
    Additionally, some information on way geometries (e.g: bus and cycle route
    info) comes only or mostly from the route relations.
    """

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
