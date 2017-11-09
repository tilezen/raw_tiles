from raw_tiles.util import time_block


def convert_rels_null_tags_to_empty_list(row):
    assert len(row) == 6, 'Unexpected number of columns: %d' % len(row)
    if row[5] is None:
        row[5] = []
    return row


class OsmSource(object):

    def __init__(self, table_prefix='planet_osm_'):
        self.table_prefix = table_prefix

    def __call__(self, table_reader, tile):
        source_locations = []
        timing = {}

        st_box2d = tile.box2d()
        for suffix in ('point', 'line', 'polygon'):
            table = self.table_prefix + suffix
            with time_block(timing, table):
                base_table_data = table_reader.read_table(
                    'base_table.sql', table, st_box2d=st_box2d)
            source_locations.append(base_table_data)

        # set up temporary tables that relations and ways will both
        # need and share info.
        with time_block(timing, 'setup'):
            table_reader.execute_template_query(
                'setup.sql', box=st_box2d)

        with time_block(timing, 'planet_osm_ways'):
            ways_table = table_reader.read_table(
                'ways.sql', 'planet_osm_ways')
        source_locations.append(ways_table)

        with time_block(timing, 'planet_osm_rels'):
            rels_table = table_reader.read_table(
                'relations.sql', 'planet_osm_rels',
                row_transform=convert_rels_null_tags_to_empty_list
            )
        source_locations.append(rels_table)

        return source_locations, timing
