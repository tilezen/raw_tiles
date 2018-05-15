SELECT
    gid AS __id__,
    ST_AsBinary(geom) AS __geometry__,
    jsonb_build_object(
      'source', 'openstreetmap.org',
      'kind', 'admin_area',
      'admin_level', 2,
      'iso_code', iso_code
    ) AS __properties__

FROM (
  SELECT
    gid,
    -- extract only polygons. we might get linestring and point fragments when
    -- the box and geometry touch but don't overlap. we don't want these, so
    -- want to throw them away.
    ST_CollectionExtract(ST_Intersection(the_geom, {{box}}), 3) AS geom,
    iso_code

  FROM admin_areas

  WHERE
    the_geom && {{box}} AND
    -- NOTE: this isn't a typo, it's the result of importing this from a shape
    -- file, where column names are only allowed to be 8 characters wide!
    admin_leve = '2'
) maybe_empty_intersections

WHERE
  NOT ST_IsEmpty(geom)
