SELECT w.id, nodes, tags
FROM planet_osm_ways w
JOIN way_ids u ON w.id = u.fid;
