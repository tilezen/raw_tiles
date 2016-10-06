Raw Tiles
=========

Raw tiles are raw extracts of a particular database table at a given zoom.
These are stored in a gzipped [msgpack](http://msgpack.org/index.html) format.

Items within the file are stored as an array of three elements:

1. The feature's ID, which should be an integral number.
2. The feature's geometry, encoded as [Well-Known Binary](https://en.wikipedia.org/wiki/Well-known_text).
3. The feature's properties, encoded as a native msgpack map.

These are then stored somewhere, for example S3, to be used by other layers in
the tile rendering pipeline.
