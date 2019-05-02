SELECT
  w.id AS id,
  hstore_to_json(w.tags) AS properties
FROM wikidata w
JOIN
  (
    SELECT DISTINCT tags->'wikidata' AS wikidata
    FROM planet_osm_point
    WHERE way && {{box}} AND tags ? 'wikidata'

    UNION

    SELECT DISTINCT tags->'wikidata' AS wikidata
    FROM planet_osm_line
    WHERE way && {{box}} AND tags ? 'wikidata'

    UNION

    SELECT DISTINCT tags->'wikidata' AS wikidata
    FROM planet_osm_polygon
    WHERE way && {{box}} AND tags ? 'wikidata'
  ) x
ON w.id = x.wikidata;
