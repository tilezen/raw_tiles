from jinja2 import Environment, PackageLoader
from raw_tiles import SourceLocation


class OsmSource(object):

    def __init__(self, conn_ctx, table_prefix='planet_osm_'):
        # TODO maybe abstract out the environment a bit?
        # templates can be reloaded in dev and cached in prod
        self.conn_ctx = conn_ctx
        self.env = Environment(
            loader=PackageLoader('raw_tiles', 'source')
        )
        self.table_prefix = table_prefix

    def read_table(self, cur, template_name, table, st_box2d=None):
        template = self.env.get_template(template_name)
        query = template.render(table=table, box=st_box2d)
        cur.execute(query)

        rows = []
        for row in cur:
            fully_read_row = []
            for col in row:
                if isinstance(col, buffer):
                    read_col = bytes(col)
                else:
                    read_col = col
                fully_read_row.append(read_col)
            rows.append(tuple(fully_read_row))

        return SourceLocation(table, rows)

    def __call__(self, tile):
        st_box2d = tile.box2d()
        # grab connection
        with self.conn_ctx() as conn:
            # commit transaction
            with conn as conn:
                # cleanup cursor resources
                with conn.cursor() as cur:

                    for suffix in ('point', 'line', 'polygon'):
                        table = self.table_prefix + suffix
                        base_table_data = self.read_table(
                                cur, 'base_table.sql', table, st_box2d)
                        yield base_table_data

                    # set up temporary tables that relations and ways will both
                    # need and share info.
                    tmp = self.env.get_template('setup.sql')
                    query = tmp.render(box=st_box2d)
                    cur.execute(query)

                    ways_table = self.read_table(
                            cur, 'ways.sql', 'planet_osm_ways')
                    yield ways_table

                    rels_table = self.read_table(
                            cur, 'relations.sql', 'planet_osm_rels')
                    yield rels_table
