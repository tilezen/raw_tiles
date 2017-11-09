from raw_tiles.formatter.msgpack import Msgpack
from raw_tiles.gen import RawrGenerator
from raw_tiles.sink.local import LocalSink
from raw_tiles.source.conn import ConnectionContextManager
from raw_tiles.source.generic import GenericTableSource
from raw_tiles.source.multi import MultiSource
from raw_tiles.source.osm import OsmSource
from raw_tiles.source.table_reader import TableReader
from raw_tiles.tile import Tile


def parse_range(z, args):
    """
    Parse args, a string representing a range of tile coordinates (either x or
    y), at zoom level z.

    Supported formats are:
      - '*' for all coordinates at that zoom.
      - A single number for a single coordinate.
      - A range of numbers separated by a dash, inclusive of both ends.

    Returns a generator over the coordinates.
    """

    assert len(args) == 1
    arg = args[0]

    if arg == "*":
        return xrange(0, 2**z - 1)
    r = map(int, arg.split('-'))
    if len(r) == 1:
        r = [r[0], r[0]]
    elif len(r) != 2:
        raise RuntimeError('Expected either a single value or a range '
                           'separated by a dash. Did not understand %r' %
                           (arg,))
    # range is inclusive, but xrange is exclusive of the last parameter, so
    # need to shift it by one.
    lo, hi = r
    return xrange(lo, hi + 1)


def raw_tiles_main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate RAWR tiles')
    parser.add_argument('zoom', metavar='Z', type=int, nargs=1,
                        help='The zoom level.')
    parser.add_argument('x', metavar='X', nargs=1,
                        help='The x coordinate, or coordinate range '
                        '(e.g: 0-8). Use * to indicate the whole range.')
    parser.add_argument('y', metavar='Y', nargs=1,
                        help='The y coordinate, or coordinate range '
                        '(e.g: 0-8). Use * to indicate the whole range.')

    parser.add_argument('--dbparams', help='Database parameters')
    parser.add_argument('--sources', nargs='?',
                        default='osm,wof',
                        help='The comma-separated list of sources to create '
                        'RAWR tiles from.')

    # TODO: build WOF & SHP on top of the generic table source.
    # TODO: tests for the generic table source

    args = parser.parse_args()

    z = int(args.zoom[0])
    x_range = parse_range(z, args.x)
    y_range = parse_range(z, args.y)

    conn_ctx = ConnectionContextManager(args.dbparams)

    sources = []
    for source_name in args.sources.split(','):
        if source_name == 'osm':
            sources.append(OsmSource())
        elif source_name == 'wof':
            sources.append(GenericTableSource('wof'))
        elif source_name == 'water_polygons':
            sources.append(GenericTableSource(
                'water_polygons', bbox_expansion_factor=1.1))
        elif source_name == 'land_polygons':
            sources.append(GenericTableSource('land_polygons'))
        else:
            raise ValueError('No known source with name %r' % (source_name,))

    src = MultiSource(sources)
    fmt = Msgpack()
    sink = LocalSink('tiles', '.msgpack')
    rawr_gen = RawrGenerator(src, fmt, sink)

    # grab connection
    with conn_ctx() as conn:
        # commit transaction
        with conn as conn:
            # cleanup cursor resources
            with conn.cursor() as cur:
                table_reader = TableReader(cur)

                for x in x_range:
                    for y in y_range:
                        tile = Tile(z, x, y)
                        rawr_gen(table_reader, tile)


if __name__ == '__main__':
    raw_tiles_main()
