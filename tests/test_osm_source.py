import unittest


class MockTableReader(object):

    def __init__(self):
        self.executed = []
        self.read = []

    def execute_template_query(self, template_name, **kwargs):
        self.executed.append((template_name, kwargs))

    def read_table(self, template_name, table_name, **kwargs):
        from raw_tiles import SourceLocation
        # don't count row_transform as a kwarg for the purposes of testing as
        # it's not passed to the template
        kwargs.pop('row_transform', None)
        self.executed.append((template_name, kwargs))
        self.read.append(table_name)
        return SourceLocation(table_name, [])


class TestOsmSource(unittest.TestCase):

    def test_osm_source(self):
        from raw_tiles.source.osm import OsmSource
        from raw_tiles.tile import Tile

        reader = MockTableReader()
        src = OsmSource()
        locations, timing = src(reader, Tile(0, 0, 0))

        self.assertEqual([
            'planet_osm_point',
            'planet_osm_line',
            'planet_osm_polygon',
            'planet_osm_ways',
            'planet_osm_rels',
            ], [location.name for location in locations])
        for location in locations:
            self.assertEqual([], location.records)

        # should have 6 executions of templates - one for each table, plus one
        # for "setup.sql"
        expected_executions = [
            ('base_table.sql', ['st_box2d']),  # planet_osm_point
            ('base_table.sql', ['st_box2d']),  # planet_osm_line
            ('base_table.sql', ['st_box2d']),  # planet_osm_polygon
            ('setup.sql', ['box']),
            ('ways.sql', []),
            ('relations.sql', []),
        ]

        self.assertEqual(len(expected_executions), len(reader.executed))
        for expect, actual in zip(expected_executions, reader.executed):
            expect_sql, expect_keys = expect
            actual_sql, actual_kwargs = actual
            self.assertEqual(expect_sql, actual_sql)
            self.assertEqual(set(expect_keys), set(actual_kwargs.keys()))
