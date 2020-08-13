import unittest


class MockSource(object):

    def __init__(self, name, records, timing):
        self.name = name
        self.records = records
        self.timing = timing

    def __call__(self, table_reader, tile):
        from raw_tiles import SourceLocation
        location = SourceLocation(self.name, self.records)
        return [location], self.timing


class TestMultiSource(unittest.TestCase):

    def test_multi_source(self):
        from raw_tiles.source.multi import MultiSource
        from raw_tiles.tile import Tile

        src1 = MockSource("src1", ["record1"], {"timing1": 123})
        src2 = MockSource("src2", ["record2"], {"timing2": 321})

        multi = MultiSource([src1, src2])
        table_reader = None

        locs, times = multi(table_reader, Tile(0, 0, 0))

        self.assertEqual(2, len(locs))
        self.assertEqual("src1", locs[0].name)
        self.assertEqual(["record1"], locs[0].records)
        self.assertEqual("src2", locs[1].name)
        self.assertEqual(["record2"], locs[1].records)
        self.assertEqual(123, times.get("timing1"))
        self.assertEqual(321, times.get("timing2"))
