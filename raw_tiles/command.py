from raw_tiles.formatter.msgpack import Msgpack
from raw_tiles.formatter.gzip import Gzip
from raw_tiles.source.osm import OsmSource
from raw_tiles.sink.local import LocalSink
from raw_tiles.tile import Tile


def parse_range(z, args):
    assert len(args) == 1
    arg = args[0]

    if arg == "*":
        return [0, 2**z - 1]
    r = map(int, arg.split('-'))
    if len(r) == 1:
        r = [r[0], r[0]]
    elif len(r) != 2:
        raise RuntimeError('Expected either a single value or a range '
                           'separated by a dash. Did not understand %r' %
                           (arg,))
    return r


def range_gen(a, b):
    assert a <= b
    while a <= b:
        yield a
        a += 1


if __name__ == '__main__':
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

    args = parser.parse_args()

    z = int(args.zoom[0])
    x_range = parse_range(z, args.x)
    y_range = parse_range(z, args.y)

    src = OsmSource(args.dbparams)
    fmt = Gzip(Msgpack())
    sink = LocalSink('tiles', fmt)

    for x in range_gen(*x_range):
        for y in range_gen(*y_range):
            tile = Tile(z, x, y)
            src.write(sink, tile)
