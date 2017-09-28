CREATE TEMPORARY TABLE node_ids AS
SELECT DISTINCT osm_id AS fid
FROM planet_osm_point
WHERE way && {{box}} AND osm_id >= 0;


CREATE TEMPORARY TABLE way_ids AS
SELECT DISTINCT osm_id AS fid
FROM planet_osm_line
WHERE way && {{box}} AND osm_id >= 0

UNION DISTINCT
SELECT DISTINCT osm_id AS fid
FROM planet_osm_polygon
WHERE way && {{box}} AND osm_id >= 0;


CREATE TEMPORARY TABLE rel_ids AS
SELECT DISTINCT -osm_id AS fid
FROM planet_osm_line
WHERE way && {{box}} AND osm_id < 0

UNION DISTINCT
SELECT DISTINCT -osm_id AS fid
FROM planet_osm_polygon
WHERE way && {{box}} AND osm_id < 0;


CREATE TEMPORARY TABLE used_rel_ids AS
SELECT DISTINCT r.id
FROM planet_osm_rels r
JOIN node_ids i ON r.parts && ARRAY[i.fid]
WHERE r.parts[1:way_off] && ARRAY[i.fid]

UNION DISTINCT
SELECT DISTINCT r.id
FROM planet_osm_rels r
JOIN way_ids i ON r.parts && ARRAY[i.fid]
WHERE r.parts[way_off+1:rel_off] && ARRAY[i.fid]

UNION DISTINCT
SELECT DISTINCT r.id
FROM planet_osm_rels r
JOIN rel_ids i ON r.parts && ARRAY[i.fid]
WHERE r.parts[rel_off+1:array_upper(parts,1)] && ARRAY[i.fid];
