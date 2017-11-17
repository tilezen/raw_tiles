class MultiSource(object):

    """
    Source that combines several sources into one.

    This is useful for keeping code separate and readable, so that each source
    can be its own class rather than putting a lot of logic into a single
    class.
    """

    def __init__(self, sources):
        self.sources = sources

    def __call__(self, table_reader, tile):
        all_source_locations = []
        all_timing = {}

        for source in self.sources:
            source_locations, timing = source(table_reader, tile)
            all_source_locations.extend(source_locations)
            all_timing.update(timing)

        return all_source_locations, all_timing
