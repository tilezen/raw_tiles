import unittest


class TileTest(unittest.TestCase):

    def test_parent(self):
        from raw_tiles.tile import Tile
        self.assertEquals(Tile(0, 0, 0), Tile(1, 0, 0).parent())
        self.assertEquals(Tile(1, 0, 0), Tile(2, 1, 1).parent())

    def test_coverage_trivial(self):
        # test that the trivial coverage - a tile's shape with itself as the
        # parent - returns that single tile.

        from raw_tiles.tile import Tile, shape_tile_coverage

        t = Tile(10, 255, 123)
        cov = shape_tile_coverage(t.as_shapely(), 10, t)
        self.assertEquals(1, len(cov))
        self.assertEquals(set([t]), cov)

    def test_coverage_pyramid(self):
        # test that the coverage of a tile over its own shape at a different
        # zoom returns all the tiles at the base of the pyramid.

        from raw_tiles.tile import Tile, shape_tile_coverage

        t = Tile(10, 255, 123)
        cov = shape_tile_coverage(t.as_shapely(), 12, t)
        self.assertEquals(16, len(cov))
        expected = set()
        for x in range(1020, 1024):
            for y in range(492, 496):
                expected.add(Tile(12, x, y))
        self.assertEquals(expected, cov)

    def test_coverage_point(self):
        # test the coverage of a simple point object, which will generally be
        # a single tile, unless it's on the border of two tiles, or the corner
        # of 4.

        from raw_tiles.tile import Tile, shape_tile_coverage
        from shapely.geometry.point import Point

        # -122.4112, 37.7454
        pt = Point(-13626752.45, 4543521.54)
        cov = shape_tile_coverage(pt, 16, Tile(0, 0, 0))
        self.assertEquals(1, len(cov))
        self.assertEquals(set([Tile(16, 10483, 25337)]), cov)

    def test_coverage_null_island(self):
        # null island at (0, 0) should hit 4 tiles, since it's on the corner.

        from raw_tiles.tile import Tile, shape_tile_coverage
        from shapely.geometry.point import Point

        pt = Point(0, 0)
        cov = shape_tile_coverage(pt, 16, Tile(0, 0, 0))
        self.assertEquals(4, len(cov))
        expected = set([
            Tile(16, 32767, 32767),
            Tile(16, 32767, 32768),
            Tile(16, 32768, 32767),
            Tile(16, 32768, 32768),
        ])
        self.assertEquals(expected, cov)
