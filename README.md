Raw Tiles
=========

Raw tiles are raw extracts of a particular database table at a given zoom. These are stored in a gzipped [msgpack](http://msgpack.org/index.html) format.

For "standard" geographic tables, items within the file are stored as an array of three elements:

1. The feature's ID, which should be an integral number.
2. The feature's geometry, encoded as [Well-Known Binary](https://en.wikipedia.org/wiki/Well-known_text).
3. The feature's properties, encoded as a native msgpack map.

Two auxilliary tables are also used; `planet_osm_ways` and `planet_osm_rels`. The former stores the relationship between ways, which can be either linestring or polygon features, and the nodes which comprise them. This is used to figure out which gates are part of of highway features. The latter stores generalised "relation" relationships between elements, and is used to look up which routes go along a particular road, or figure out the structure of railway stations. The items stored within these tables are:

* `planet_osm_rels`: Relation ID, Way offset within parts, Relation offset within parts, parts array of member IDs, members array of type-prefixed member IDs paired with the member role, tags.
* `plane_osm_ways`: Way ID, nodes array of node IDs, tags.

These are then stored somewhere, for example S3, to be used by other layers in the tile rendering pipeline.

Why not just use a database?
----------------------------

The [Tilezen](https://github.com/tilezen) system originally used a [PostgreSQL](https://www.postgresql.org/) database with [PostGIS](https://postgis.net/) to provide spatial indexes. This system performs very well and is very flexible. This system worked well for Tilezen, and many other tile providers, for many years.

However, we found a couple of issues would repeatedly cause headaches; scaling and logic in the database.

### Scaling

Each tile rendered, whether batch in [tilequeue](https://github.com/tilezen/tilequeue) or on-demand in [tileserver](https://github.com/tilezen/tileserver), queries the database. This means that when there's a lot of load, due to many data changes or on-demand interest in non-cached areas, the PostgreSQL servers can become a bottleneck. Individual PostgreSQL servers scale well, and scaling out to multiple servers is possible. However, setting up each new replica server and synchronising it with the master takes a long time (around 24h in our experience), which makes it unsuitable for handling real-time load changes.

This doesn't mean that we shouldn't use PostgreSQL, just that we should find some way to take it off the "hot path".

### Logic in the database

To support efficient queries for features at a given zoom level, the Tilezen database contains [indexes](https://github.com/tilezen/vector-datasource/blob/7b7394482ccd72bb8a46f30137203ea49ce974af/data/apply-planet_osm_polygon.sql#L47) on the feature geometry and minimum zoom level that the feature is visible at. This works well, but means that the definition of which zoom level a feature is visible at must be available to the database.

Most features have a simple relationship between their tags, geometry and the `min_zoom` they are assigned. However, some features have [complex queries](https://github.com/tilezen/vector-datasource/blob/7b7394482ccd72bb8a46f30137203ea49ce974af/data/functions.sql#L580) to determine their `min_zoom`. Others have [extremely complex queries](https://mapzen.com/blog/station-relations/).

This creates a headache when deploying new versions of the style, as some deployments require a [migration](https://github.com/tilezen/vector-datasource/blob/7b7394482ccd72bb8a46f30137203ea49ce974af/data/migrations/v1.3.0-polygon.sql) to update the `min_zoom` values in the database to their new calculated values. These migrations are especially bad, as they are hand-written and therefore prone to missing things which needed to be updated. They are also hard to reverse if something goes wrong.

Finally, having logic specific to a particular version of a single style in the database makes it difficult to share that database between many different styles, or many versions of a single style. In turn, this makes "Long Term Support" releases difficult without duplicating infrastructure.


Raw(r) system design
--------------------

To solve the problems above, we want to:

* Be able to render any tile, whether batch or on-demand, without querying the database.
* Be able to render any style or any version of a style from the same data source.

To do this, we combine the [Fundamental Theorem of Software Engineering](https://en.wikipedia.org/wiki/Fundamental_theorem_of_software_engineering),

> We can solve any problem by introducing an extra level of indirection

With something that we might call the "Fundamental Theorem of Web Mapping",

> We can solve any problem by making tiles

And end up with an intermediate data store, consisting of tiles of "raw" data. These tiles would be able to render any style, or version of a style, because they contain all the data and haven't been transformed or filtered. Due to the limited geographic footprint of the tile, they inherently act as a coarse index over the data. However, to avoid querying the database, _all_ the raw(r) tiles must be available.

Low zoom levels present a problem, since rendered vector tiles at low zoom levels typically contain a tiny fraction of the total amount of data in their geographic extent. Although raw(r) tiles are not intended for client use, and we can assume a high-bandwidth datacentre network, raw(r) tiles are still not much use if the `0/0/0` tile contains the entire, multi-gigabyte dataset. Therefore, we choose to limit the "raw" data to a particular zoom level. We then need some style-aware way to construct the lower zoom levels from those.

There needs to be a balance between the number of raw(r) tiles being generated and kept up to date, which is `4^z`, and the size of each individual tile, which falls off as `4^-z`. We're hoping that a good compromise between these two will be zoom 10.

The overall system looks like:

1. A database of geographic data, possibly with updates.
2. A process which reads the database and produces raw(r) tiles, possibly in response to updates.
3. A store of raw(r) tiles which is quick to access and scales easily.
4. A batch or on-demand process which reads raw(r) tiles and calculates a `min_zoom` for each feature based on a style, producing one or more vector tiles. The vector tiles are either stored in a metatile or returned to the client. For features where `min_zoom` is smaller than z10, the batch process also emits a lower-zoom "cooked" raw(r) tile fragments.
5. A process which aggregates "cooked" raw(r) tile fragments into whole "cooked" raw(r) tiles at zoom 5. This recurses again to make the top of the pyramid; the zoom 0 "cooked" raw(r) tile.
6. A store (cache) of vector metatiles which is quick to access and scales easily.
7. A front-end [process which unpacks metatiles](https://github.com/tilezen/tapalcatl) and responds with the tile that the client requested.

Raw(r) tiles benefits
---------------------

* Since all raw(r) tiles are rendered, the database load is unrelated to tile demands. This means that a constant (and probably small) number of database servers is needed.
* Since raw(r) tiles themselves are flat files, serving them should be much easier to scale.
* Since raw(r) tiles have not been filtered, and contain no style-based information, it should be possible to run multiple versions of styles concurrently. This can be used to implement LTS versions, or to provide live previews of new versions.
* Organising the batch rendering jobs into z10 tiles to match the data should improve data locality and speed up batch tile rendering.

Raw(r) tiles drawbacks
----------------------

* Each raw(r) tile can be large, meaning a lot of data has to be parsed to extract the relevant parts for a given single tile. At the moment, indexing a large tile (`10/163/395`, contains San Francisco) takes approximately 2s - although these indexes aren't based on real style information. Current data on median database query time shows it varying between 1s and 10s, compared with around 20s for post-processing. For large tiles, the raw(r) indexing is already competitive and, if there are problems for smaller tiles then further optimisation should be able to bring this down.
* Tooling and debugging; PostgreSQL has very good tooling and is easily inspectable, but raw(r) tiles lack this and it will make debugging harder. We will probably either end up writing a set of tooling to inspect raw(r) tiles, or spending a lot of time stepping through code line-by-line.
* Complexity; introducing this layer of indirection and additional processing makes the system more complex and therefore more likely to have bugs and fail in unexpected ways. We can minimise the risk by trying to keep the system as simple and transparent as possible.


Why msgpack?
------------

Msgpack makes small files which are quick enough to parse. They don't enforce a schema, which is helpful during development, but might cause issues if the file definition changes later on.

There are other serialisation formats which could be used, but at this point have some disadvantages which makes msgpack look like a better option:

* [Google Protocol Buffers](https://developers.google.com/protocol-buffers/), which is similar to msgpack but requires a schema. This would make it more difficult to store the tags or change the "shape" of the data format.
* [Google FlatBuffers](https://google.github.io/flatbuffers/), which stores data in a `mmap`-friendly way. This means the files are somewhat larger, but that it would be possible to access data within the file more easily (e.g: sub-tiling for geographic indexing). FlatBuffers would also require a schema. It's not clear at this point whether having random access to data within the raw(r) tile would be a benefit worth trading off the file size for.
* [GeoJSON](http://geojson.org/) has a huge advantage of easy readability, but is slower to parse than the WKB stored in msgpack. Additionally, the binary to decimal conversion required to serialise the coordinates can lose precision and create broken geometries.
* [ORC](https://orc.apache.org/) is a columnar storage format designed for use with Hadoop and Hive, and is designed for extracting matching rows from a large file. However, it lacks much language support outside of Java, making it difficult to work with in the mostly-Python Tilezen system.
