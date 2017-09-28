SELECT
  osm_id AS id,
  ST_AsBinary(way) AS geometry,
  hstore_to_json(tags) AS properties
FROM {{table}}
WHERE way && {{box}};
