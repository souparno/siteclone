import sys
import unittest
from urllib.request import urlopen
from unittest.mock import patch, mock_open


class Mock():
    def __init__(self, request, context):
        return None

    def read(self):
        return self

    def decode(self, arg):
        return ''

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


with patch.object(sys, 'argv', ['', 'url', 'base_path']):

    with patch('urllib.request.urlopen',  Mock):

        with patch("builtins.open", mock_open(read_data="data")):

            from siteclone import clone


class TestClone(unittest.TestCase):

    def test_getUrl(self):
        url = "https://demo.foo.co.uk/bar/\#top"
        url = clone.getUrl(url)
        self.assertEqual(url, 'https://demo.foo.co.uk/bar/\\')

        url = "https://themes.foo.com/foo/bar/"
        url = clone.getUrl(url)
        self.assertEqual(url, 'https://themes.foo.com/foo/bar/')

        url = "https://themes.foo.com/foo/bar"
        url = clone.getUrl(url)
        self.assertEqual(url, 'https://themes.foo.com/foo/bar')

        url = "http://domain.com/foo/bar/demo.html"
        url = clone.getUrl(url)
        self.assertEqual(url, 'http://domain.com/foo/bar/demo.html')

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

