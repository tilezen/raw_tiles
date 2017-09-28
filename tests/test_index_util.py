import unittest


class IndexUtilTest(unittest.TestCase):

    def test_deassoc(self):
        from raw_tiles.index.util import deassoc
        self.assertEquals({}, deassoc([]))
        self.assertEquals({'a': 1}, deassoc(['a', 1]))
        self.assertEquals({'a': 1}, deassoc(['a', 1, 'b']))
        self.assertEquals({'a': 1, 'b': 2}, deassoc(['a', 1, 'b', 2]))
