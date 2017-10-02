from cStringIO import StringIO
from raw_tiles import FormattedData
from raw_tiles import RawrTile


class RawrGenerator(object):

    """put the pieces of rawr tile generation pipeline together"""

    def __init__(self, source, formatter, sink):
        self.source = source
        self.formatter = formatter
        self.sink = sink

    def __call__(self, tile):

        all_fmt_data = []
        for source_location in self.source(tile):
            buf = StringIO()
            writer = self.formatter.create(buf)
            for record in source_location.records:
                writer.write(record)
            writer.close()
            data = buf.getvalue()
            fmt_data = FormattedData(source_location.name, data)
            all_fmt_data.append(fmt_data)

        rawr_tile = RawrTile(tile, all_fmt_data)
        self.sink(rawr_tile)
