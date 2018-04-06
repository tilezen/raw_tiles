from raw_tiles.source.generic import GenericTableSource
from raw_tiles.source.multi import MultiSource
from raw_tiles.source.osm import OsmSource


DEFAULT_SOURCES = [
    'osm',
    'wof',
    'water_polygons',
    'land_polygons',
    'buffered_land',
    'ne_10m_urban_areas',
]


def parse_sources(source_names):
    sources = []
    for source_name in source_names:
        if source_name == 'osm':
            sources.append(OsmSource())
        elif source_name == 'wof':
            sources.append(GenericTableSource('wof_neighbourhood'))
        elif source_name == 'water_polygons':
            sources.append(GenericTableSource(
                'water_polygons', bbox_expansion_factor=1.1))
        elif source_name == 'land_polygons':
            sources.append(GenericTableSource('land_polygons'))
        elif source_name == 'buffered_land':
            sources.append(GenericTableSource('buffered_land'))
        elif source_name == 'ne_10m_urban_areas':
            sources.append(GenericTableSource('ne_10m_urban_areas'))
        else:
            raise ValueError('No known source with name %r' % (source_name,))

    # need at least one source
    assert sources

    # no point wrapping a single source
    if len(sources) == 1:
        return sources[0]

    else:
        return MultiSource(sources)
