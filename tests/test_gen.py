import unittest


class MockSource(object):

    def __init__(self, name, records):
        self.name = name
        self.records = records

    def __call__(self, table_reader, tile):
        from raw_tiles import SourceLocation
        location = SourceLocation(self.name, self.records)
        timing = {}
        return [location], timing


class MockSink(object):

    def __call__(self, tile):
        self.tile = tile


class GeneratorTest(unittest.TestCase):

    def test_round_trip(self):
        from raw_tiles.gen import RawrGenerator
        from raw_tiles.formatter.msgpack import Msgpack
        from raw_tiles.tile import Tile

        source_name = 'test'
        source_data = [(1, 'a', {'key': 'value'})]

        source = MockSource(source_name, source_data)
        formatter = Msgpack()
        sink = MockSink()
        table_reader = None

        gen = RawrGenerator(source, formatter, sink)

        tile = Tile(0, 0, 0)
        gen(table_reader, tile)

        # check the format (structures) of the returned data. should be using
        # the namedtuple types at the top level of the raw_tiles module
        from raw_tiles import RawrTile
        from raw_tiles import FormattedData

        self.assertIsInstance(sink.tile, RawrTile)
        self.assertEquals(tile, sink.tile.tile)
        self.assertEquals(1, len(sink.tile.all_formatted_data))

        formatted_data = sink.tile.all_formatted_data[0]
        self.assertIsInstance(formatted_data, FormattedData)
        self.assertEquals(source_name, formatted_data.name)
        self.assertIsInstance(formatted_data.data, (str, bytes))

        # check that the packed data contains the same thing as we put in!
        from msgpack import Unpacker
        from io import BytesIO

        unpacker = Unpacker(BytesIO(formatted_data.data))
        unpacked_data = list(unpacker)
        self.assertEquals(1, len(unpacked_data))
        source_datum = source_data[0]
        unpacked_datum = unpacked_data[0]
        # expect that the unpacked version has been turned into a list, but
        # is otherwise identical in contents.
        self.assertEquals(source_datum, tuple(unpacked_datum))
