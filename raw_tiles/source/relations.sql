WITH RECURSIVE upward_search(level,path,id,parts,rel_off,cycle) AS (
    SELECT 0,ARRAY[por.id],por.id,por.parts,por.rel_off,false
    FROM planet_osm_rels por
    JOIN used_rel_ids uri ON por.id = uri.id
  UNION
    SELECT
      level + 1,
      path || r.id,
      r.id,
      r.parts,
      r.rel_off,
      r.id = ANY(path)
    FROM
      planet_osm_rels r JOIN upward_search s
    ON
      ARRAY[s.id] && r.parts
    WHERE
      ARRAY[s.id] && r.parts[r.rel_off+1:array_upper(r.parts,1)] AND
      NOT cycle
  )
SELECT r.id, way_off, rel_off, parts, members, tags
FROM planet_osm_rels r
WHERE r.id IN (SELECT DISTINCT id FROM upward_search)
