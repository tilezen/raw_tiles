SELECT
  osm_id AS id,
  way AS geometry,
  hstore_to_json(tags) AS properties
FROM {{table}}
WHERE way && {{box}};
