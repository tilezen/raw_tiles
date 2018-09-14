v1.0.0
------

* Added this `CHANGELOG.md`.
* Added comment explaining why 'admin_leve' confusingly doesn't have an 'l' on the end. [PR #24](https://github.com/tilezen/raw_tiles/pull/24).
* Fix buffered land SQL (removed extra trailing comma, corrected geometry column name).
* More information about which table SQL query failures relate to during RAWR generation.
* Add admin area polygons to the RAWR tiles.
* Add architecture diagram and brief documentation. [PR #23](https://github.com/tilezen/raw_tiles/pull/23).
* When the database connection parameters give the database as a list, choose a random entry. This allows a sort of non-adaptive load-balancing. [PR #22](https://github.com/tilezen/raw_tiles/pull/22).
* Adjust WOF source name (now `.org`, not `.mapzen.com`). [PR #21](https://github.com/tilezen/raw_tiles/pull/21).
* Need to set kind and maritime_boundary for buffered land polygons. Looks like the vector-datasource filters and transforms look for those properties. [PR #20](https://github.com/tilezen/raw_tiles/pull/20).
* Add buffered land table source SQL
* Add `buffered_land` to RAWR sources default
* Create `LICENSE.md` (MIT).
