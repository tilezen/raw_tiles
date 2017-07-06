from shapely.geometry import mapping, shape
import json
from contextlib import contextmanager


class Writer:
    def __init__(self, io):
        self.io = io
        self.rownum = 0

        io.write("""{"type":"FeatureCollection","features":[""")

    def write(self, fid, wkb, props):
        feature = {
            'id': fid,
            'type': 'Feature',
            'geometry': mapping(wkb.loads(wkb)),
            'properties': props
        }

        if self.rownum > 0:
            self.io.write(',')
        self.rownum += 1

        self.io.write(json.dumps(feature, separators=(',', ':')))

    def close(self):
        self.io.write("]}")


@contextmanager
def write(io):
    w = Writer(io)
    yield w
    w.close()


def read(io):
    data = json.load(io)
    for f in data['features']:
        fid = f['id']
        geom = shape(f['geometry'])
        props = f['properties']

        yield (fid, geom, props)
