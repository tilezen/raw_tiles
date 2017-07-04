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

    def _write_base_tables(self, cur, make_file_fn, st_box2d):
        base_table = self.env.get_template('base_table.sql')

        for suffix in ('point', 'line', 'polygon'):
            table = self.table_prefix + suffix
            query = base_table.render(table=table, box=st_box2d)
            cur.execute(query)

            with make_file_fn(table) as fh:
                for row in cur:
                    fh.write(*row)

    def _write_relations(self, cur, make_file_fn, st_box2d):
        relations = self.env.get_template('relations.sql')
        query = relations.render(box=st_box2d)
        cur.execute(query)

        table = 'planet_osm_rels'
        with make_file_fn(table) as fh:
            for row in cur:
                fh.write(*row)

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
            self._write_relations(cur, make_file, st_box2d)
