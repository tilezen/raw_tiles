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
