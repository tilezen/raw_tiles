v1.1.0
------

* Change the `source` for OSM land/water polygons. The data which used to be at OpenStreetMapData.com is now hosted by FOSSGIS at osmdata.openstreetmap.de. [PR #30](https://github.com/tilezen/raw_tiles/pull/30)
* Added the `wikidata` "table" in RAWR tiles. This adds properties from the [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) project to enrich the data we have about airports (although there's nothing airport-specific about the `raw_tiles` part the code). [PR #31](https://github.com/tilezen/raw_tiles/pull/31)
* Include WOF wikidata ID in the RAWR tile to match the `vector-datasource` queries. [PR #32](https://github.com/tilezen/raw_tiles/pull/32)
* Add disputed admin capitals from Natural Earth as a type of "wikidata". This pulls in the `FCLASS_*` and `FEATURECLA` from Natural Earth, so that we can backfill this data where it's not present in OSM and also apply viewpoints. [PR #33](https://github.com/tilezen/raw_tiles/pull/33) and [PR #34](https://github.com/tilezen/raw_tiles/pull/34)

v1.0.1
------

* Update `setup.py` version to match tagged version. [PR #28](https://github.com/tilezen/raw_tiles/pull/28) and [Issue #27](https://github.com/tilezen/raw_tiles/issues/27).

v1.0.0
------

* Add this `CHANGELOG.md`.
* Add MIT licence text in `LICENSE.md`.
* Adjust WOF source name (now `.org`, not `.mapzen.com`). [PR #21](https://github.com/tilezen/raw_tiles/pull/21).
* Add **buffered_land** table to RAWR sources default with source SQL needed to set `kind` and `maritime_boundary` required for vector-datasource filters and transforms. [PR #20](https://github.com/tilezen/raw_tiles/pull/20).
* Add **admin area polygons** to the RAWR tiles (for roads and POIs country lookup), with comment explaining why 'admin_leve' confusingly doesn't have an 'l' on the end. [PR #24](https://github.com/tilezen/raw_tiles/pull/24).
* When the database connection parameters give the database as a list, choose a random entry. This allows a sort of non-adaptive load-balancing. [PR #22](https://github.com/tilezen/raw_tiles/pull/22).
* More debug information about which table SQL query failures relate to during RAWR generation.
* Add architecture diagram and brief documentation. [PR #23](https://github.com/tilezen/raw_tiles/pull/23).

v0.1.0
------

* Initial alpha release
