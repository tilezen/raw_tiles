from collections import namedtuple


# represents a particular source location, eg data from a postgresql table
SourceLocation = namedtuple('SourceLocation', 'name records')

# contains a name associated with data that has been formatted
FormattedData = namedtuple('FormattedData', 'name data')

# Container for a particular tile, and the formatted data within it
RawrTile = namedtuple('RawrTile', 'tile all_formatted_data')
