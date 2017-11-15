SELECT
    gid AS __id__,
    ST_AsBinary(ST_Intersection(the_geom, {{box}})) AS __geometry__,
    jsonb_build_object(
      'source', 'openstreetmapdata.com',
      'area', way_area,
      'min_zoom', mz_earth_min_zoom
    ) AS __properties__

FROM land_polygons

WHERE
    the_geom && {{box}}
