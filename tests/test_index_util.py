import unittest


class IndexUtilTest(unittest.TestCase):

    def test_deassoc(self):
        from raw_tiles.index.util import deassoc
        self.assertEqual({}, deassoc([]))
        self.assertEqual({'a': 1}, deassoc(['a', 1]))
        self.assertEqual({'a': 1}, deassoc(['a', 1, 'b']))
        self.assertEqual({'a': 1, 'b': 2}, deassoc(['a', 1, 'b', 2]))
