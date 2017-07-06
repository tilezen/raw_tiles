from __future__ import absolute_import
from collections import namedtuple, defaultdict
from raw_tiles.tile import shape_tile_coverage
from math import floor
from shapely.wkb import loads as wkb_loads


Feature = namedtuple('Feature', 'id geometry properties')


class _LazyShape(object):

    def __init__(self, wkb):
        self.wkb = wkb
        self.obj = None

    def __getattr__(self, name):
        if self.obj is None:
            self.obj = wkb_loads(self.wkb)
        return getattr(self.obj, name)


class FeatureTileIndex(object):

    def __init__(self, root_tile, max_z, min_zoom_fn):
        assert max_z >= root_tile.z
        self.root_tile = root_tile
        self.max_z = max_z
        self.min_zoom_fn = min_zoom_fn

        self.tile_index = defaultdict(list)

    def add_feature(self, fid, shape_wkb, props):
        # the incoming shape will be WKB and we need to parse it.
        shape = _LazyShape(shape_wkb)

        # calculate min zoom for the feature. if the min zoom is None, that
        # indicates that the feature doesn't appear at all.
        min_zoom = self.min_zoom_fn(fid, shape, props)
        if min_zoom is None:
            return

        # take the minimum integer zoom - this is the min zoom tile that the
        # feature should appear in, and a feature with min_zoom = 1.9 should
        # appear in a tile at z=1, not 2, since the tile at z=N is used for
        # the zoom range N to N+1.
        #
        # we cut this off at this index's min zoom, as we aren't interested
        # in any tiles outside of that.
        floor_zoom = max(self.root_tile.z, int(floor(min_zoom)))

        # seed initial set of tiles at maximum zoom. all features appear at
        # least at the max zoom, even if the min_zoom function returns a
        # value larger than the max zoom.
        zoom = self.max_z
        tiles = shape_tile_coverage(shape, zoom, self.root_tile)

        # merge min_zoom into the feature's properties. note that there's only
        # one copy of this, and the reference should be shared amongst many
        # entries in the tile index.
        feature = Feature(fid, shape, props.copy())
        feature.properties['min_zoom'] = min_zoom

        while zoom >= floor_zoom:
            parent_tiles = set()
            for tile in tiles:
                self.tile_index[tile].append(feature)
                parent_tiles.add(tile.parent())

            zoom -= 1
            tiles = parent_tiles

    def __call__(self, tile):
        return self.tile_index.get(tile, [])
