SELECT
    wof_id AS __id__,
    ST_AsBinary(label_position) AS __geometry__,

    COALESCE(to_jsonb(l10n_name), '{}'::jsonb) ||
    jsonb_build_object(
      'name', name,
      'source', 'whosonfirst.org',
      'mz_n_photos', n_photos,
      'area', area,
      'is_landuse_aoi', is_landuse_aoi,
      'placetype', wof_np.placetype_string,
      'min_zoom', min_zoom,
      'max_zoom', max_zoom
    ) AS __properties__

FROM wof_neighbourhood wof_n

INNER JOIN wof_neighbourhood_placetype wof_np ON wof_n.placetype = wof_np.placetype_code

WHERE
  wof_n.is_visible AND
  label_position && {{box}}
