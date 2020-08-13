from raw_tiles.util import bbox_for_tile
from raw_tiles.util import st_box2d_for_bbox
from raw_tiles.util import time_block
from sys import exc_info


# returns a geometry which is the given bounds expanded by `factor`. that is,
# if the original shape was a 1x1 box, the new one will be `factor`x`factor`
# box, with the same centroid as the original box.
#
# TODO: this is almost a copy-paste from tilequeue because i didn't want to
# introduce an "upward" dependency. looks like this would be a good candidate
# for moving to a "tilezen util" library.
def calculate_padded_bounds(factor, bounds):
    min_x, min_y, max_x, max_y = bounds
    dx = 0.5 * (max_x - min_x) * (factor - 1.0)
    dy = 0.5 * (max_y - min_y) * (factor - 1.0)
    return min_x - dx, min_y - dy, max_x + dx, max_y + dy


class GenericTableSource(object):

    def __init__(self, table_name, bbox_expansion_factor=None):
        self.table_name = table_name
        self.bbox_expansion_factor = bbox_expansion_factor

    def __call__(self, table_reader, tile):
        source_locations = []
        timing = {}

        with time_block(timing, self.table_name):

            if self.bbox_expansion_factor:
                bounds = bbox_for_tile(tile.z, tile.x, tile.y)
                padded_bounds = calculate_padded_bounds(
                    self.bbox_expansion_factor, bounds)
                box2d = st_box2d_for_bbox(padded_bounds)

            else:
                box2d = tile.box2d()

            template_name = self.table_name + ".sql"

            try:
                table = table_reader.read_table(
                    template_name, self.table_name, st_box2d=box2d)
            except Exception as e:
                raise type(e)('%s in table %r' % (str(e), self.table_name))\
                    .with_traceback(exc_info()[2])

        source_locations.append(table)

        return source_locations, timing
