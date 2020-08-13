from raw_tiles import SourceLocation
from jinja2 import Environment, PackageLoader


class TableReader(object):

    def __init__(self, cur):
        self.env = Environment(
            loader=PackageLoader('raw_tiles', 'source')
        )
        self.cur = cur

    def execute_template_query(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        query = template.render(**kwargs)
        self.cur.execute(query)

    def read_table(self, template_name, table_name,
                   st_box2d=None, row_transform=None):
        self.execute_template_query(
            template_name, table=table_name, box=st_box2d)

        rows = []
        for row in self.cur:
            fully_read_row = []
            for col in row:
                read_col = col
                fully_read_row.append(read_col)
            if row_transform is not None:
                fully_read_row = row_transform(fully_read_row)
            rows.append(tuple(fully_read_row))

        return SourceLocation(table_name, rows)
