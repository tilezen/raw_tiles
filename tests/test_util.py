import unittest


class UtilTest(unittest.TestCase):

    def test_bbox_for_tile(self):
        from raw_tiles.util import bbox_for_tile, MERCATOR_WORLD_SIZE
        c = 0.5 * MERCATOR_WORLD_SIZE
        self.assertEqual((-c, -c, c, c), bbox_for_tile(0, 0, 0))
        self.assertEqual((-c,  0, 0, c), bbox_for_tile(1, 0, 0))
        self.assertEqual((-c, -c, 0, 0), bbox_for_tile(1, 0, 1))
        self.assertEqual((0,   0, c, c), bbox_for_tile(1, 1, 0))
        self.assertEqual((0,  -c, c, 0), bbox_for_tile(1, 1, 1))
