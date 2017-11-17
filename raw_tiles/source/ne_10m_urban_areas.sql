SELECT

  gid AS __id__,

  ST_AsBinary(the_geom) AS __geometry__,

  jsonb_build_object(
    'area', way_area,
    'kind', 'urban_area'
  ) AS __properties__

FROM ne_10m_urban_areas

WHERE
  the_geom && {{box}}
