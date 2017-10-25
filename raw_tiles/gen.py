from cStringIO import StringIO
from raw_tiles import FormattedData
from raw_tiles import RawrTile
from raw_tiles.util import time_block


class RawrGenerator(object):

    """put the pieces of rawr tile generation pipeline together"""

    def __init__(self, source, formatter, sink):
        self.source = source
        self.formatter = formatter
        self.sink = sink

    def __call__(self, tile):

        timing = {}

        source_timing = {}
        with time_block(source_timing, 'total'):
            source_locations, source_specific_timing = self.source(tile)
        source_timing.update(source_specific_timing)
        timing['source'] = source_timing

        all_fmt_data = []
        format_timing = {}
        with time_block(format_timing, 'total'):
            for source_location in source_locations:
                with time_block(format_timing, source_location.name):
                    buf = StringIO()
                    writer = self.formatter.create(buf)
                    for record in source_location.records:
                        # record is a tuple here, and writer.write takes
                        # varargs, so we need to unpack the tuple.
                        writer.write(*record)
                    writer.flush()
                    data = buf.getvalue()
                    # close writer after we get the buffer value, so that the
                    # writer hasn't closed the buffer yet.
                    writer.close()
                    fmt_data = FormattedData(source_location.name, data)
                    all_fmt_data.append(fmt_data)
        timing['format'] = format_timing

        with time_block(timing, 'sink'):
            rawr_tile = RawrTile(tile, all_fmt_data)
            self.sink(rawr_tile)

        return timing
