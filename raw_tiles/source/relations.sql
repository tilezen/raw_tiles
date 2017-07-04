SELECT r.id, way_off, rel_off, parts, members, tags
FROM planet_osm_rels r
JOIN used_rel_ids u ON r.id = u.id;
