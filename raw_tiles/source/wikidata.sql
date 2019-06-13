WITH wikidata_ids AS (
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
)
SELECT
  x.wikidata AS id,
  hstore_to_json(coalesce(w.tags, ''::hstore) || coalesce(p.tags, ''::hstore)) AS properties
FROM wikidata_ids x
LEFT JOIN wikidata w ON w.id = x.wikidata
LEFT JOIN (
  -- this grabs the wikidata, hstore(fclass_*) data, omitting null values for
  -- fclass_*, which makes the data smaller and easier to read.
  SELECT wikidataid, hstore(array_agg(key), array_agg(value)) AS tags
  FROM (
    SELECT * FROM (
      SELECT wikidataid, (each(hstore(ne_pp))).key, (each(hstore(ne_pp))).value
      FROM ne_10m_populated_places ne_pp
    ) x WHERE (key = 'featurecla' OR key LIKE 'fclass_%') AND VALUE IS NOT NULL
  ) y GROUP BY wikidataid
) p ON p.wikidataid = x.wikidata;
