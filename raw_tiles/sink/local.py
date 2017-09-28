import errno
import os
from io import open


# from https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python#600612 # noqa
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class LocalSink(object):

    def __init__(self, base_dir, formatter):
        self.base_dir = base_dir
        self.formatter = formatter

    def create_file(self, schema, table, tile):
        file_dir = os.path.join(self.base_dir, schema, table,
                                str(tile.z), str(tile.x))
        ext = self.formatter.extension()

        # ensure directory exists to take tile file
        mkdir_p(file_dir)

        io = open(os.path.join(file_dir, "%d.%s" % (tile.y, ext)), 'wb')
        return self.formatter.create(io)
