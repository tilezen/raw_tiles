from time import time


MERCATOR_WORLD_SIZE = 40075016.68


def bbox_for_tile(z, x, y):
    max_coord = float(1 << z)
    return (
        ((x / max_coord) - 0.5) * MERCATOR_WORLD_SIZE,
        (0.5 - ((y + 1) / max_coord)) * MERCATOR_WORLD_SIZE,
        (((x + 1) / max_coord) - 0.5) * MERCATOR_WORLD_SIZE,
        (0.5 - (y / max_coord)) * MERCATOR_WORLD_SIZE)


def st_box2d_for_bbox(bbox):
    return "st_setsrid(st_makebox2d(st_point(%f, %f), " \
        "st_point(%f, %f)), 3857)" % bbox


def st_box2d_for_tile(z, x, y):
    return st_box2d_for_bbox(bbox_for_tile(z, x, y))


# TODO this was lifted from tilequeue
# if we grow a utility repo we can just move this sort of thing there
class time_block(object):

    """Convenience to capture timing information"""

    def __init__(self, timing_state, key):
        # timing_state should be a dictionary
        self.timing_state = timing_state
        self.key = key

    def __enter__(self):
        self.start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        stop = time()
        duration_seconds = stop - self.start
        duration_millis = duration_seconds * 1000
        self.timing_state[self.key] = duration_millis
