SELECT
    gid AS __id__,
    ST_AsBinary(geom) AS __geometry__,
    jsonb_build_object(
      'source', 'openstreetmapdata.com',
      'area', way_area,
      'min_zoom', mz_earth_min_zoom
    ) AS __properties__

FROM (
  SELECT
    gid,
    -- extract only polygons. we might get linestring and point fragments when
    -- the box and geometry touch but don't overlap. we don't want these, so
    -- want to throw them away.
    ST_CollectionExtract(ST_Intersection(the_geom, {{box}}), 3) AS geom,
    way_area,
    mz_earth_min_zoom

  FROM land_polygons

  WHERE
    the_geom && {{box}}
) maybe_empty_intersections

WHERE
  NOT ST_IsEmpty(geom)
