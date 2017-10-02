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

    def __init__(self, base_dir, ext):
        self.base_dir = base_dir
        self.ext = ext

    def make_fs_path(self, tile, fmt_name):
        """return a pair of directory and filename paths"""
        file_dir = os.path.join(self.base_dir, fmt_name,
                                str(tile.z), str(tile.x))
        path = os.path.join(file_dir, '%d%s' % (tile.y, self.ext))
        return file_dir, path

    def __call__(self, rawr_tile):
        for fmt_data in rawr_tile.all_formatted_data:
            dir_path, file_path = self.make_fs_path(
                    rawr_tile.tile, fmt_data.name)
            mkdir_p(dir_path)
            with open(file_path, 'wb') as fp:
                fp.write(fmt_data.data)
