from jinja2 import Environment, PackageLoader
import psycopg2
from contextlib import contextmanager


class OsmSource(object):
    def __init__(self, dbparams, table_prefix='planet_osm_'):
        self.env = Environment(
            loader=PackageLoader('raw_tiles', 'source')
        )
        self.table_prefix = table_prefix
        self.dbparams = dbparams

    def _write_table(self, cur, make_file_fn, template, table, st_box2d=None):
        tmp = self.env.get_template(template)
        query = tmp.render(table=table, box=st_box2d)
        cur.execute(query)

        with make_file_fn(table) as fh:
            for row in cur:
                fh.write(*row)

    def _write_base_tables(self, cur, make_file_fn, st_box2d):
        for suffix in ('point', 'line', 'polygon'):
            table = self.table_prefix + suffix
            self._write_table(cur, make_file_fn, 'base_table.sql', table,
                              st_box2d)

    def _write_ways(self, cur, make_file_fn):
        self._write_table(cur, make_file_fn, 'ways.sql', 'planet_osm_ways')

    def _write_relations(self, cur, make_file_fn):
        self._write_table(cur, make_file_fn, 'relations.sql',
                          'planet_osm_rels')

    def write(self, sink, tile):
        st_box2d = tile.box2d()
        conn = psycopg2.connect(self.dbparams)

        @contextmanager
        def make_file(table):
            fh = sink.create_file('osm', table, tile)
            yield fh
            fh.close()

        with conn.cursor() as cur:
            self._write_base_tables(cur, make_file, st_box2d)

            # set up temporary tables that relations and ways will both need
            # and share info.
            tmp = self.env.get_template('setup.sql')
            query = tmp.render(box=st_box2d)
            cur.execute(query)

            self._write_ways(cur, make_file)
            self._write_relations(cur, make_file)
