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


with patch.object(sys, 'argv', ['', '', 'base_path']):

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

    def test_cleanPath(self):
        #  clean /// -> /
        path = clone.cleanPath("demo.foo.co.uk/bar///assets/images/menu.png")
        self.assertEqual(path, "demo.foo.co.uk/bar/assets/images/menu.png")

        #  clean /./ -> /
        path = clone.cleanPath("demo.foo.co.uk/bar/assets/./images/menu.png")
        self.assertEqual(path, "demo.foo.co.uk/bar/assets/images/menu.png")

        #  clean \\/ -> /
        path = clone.cleanPath("demo.foo.co.uk/bar\\/assets/images/menu.png")
        self.assertEqual(path, "demo.foo.co.uk/bar/assets/images/menu.png")

        #  clean \/ -> /
        path = clone.cleanPath("demo.foo.co.uk/bar\/assets/images/menu.png")
        self.assertEqual(path, "demo.foo.co.uk/bar/assets/images/menu.png")

    def test_groupUrl(self):
        path = clone.groupUrl("https://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path.group(1), "https://")
        self.assertEqual(path.group(2), "demo.foo.co.uk/bar/assets/images/menu.png")

        path = clone.groupUrl("http://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path.group(1), "http://")
        self.assertEqual(path.group(2), "demo.foo.co.uk/bar/assets/images/menu.png")

        path = clone.groupUrl("//demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path.group(1), "//")
        self.assertEqual(path.group(2), "demo.foo.co.uk/bar/assets/images/menu.png")

        path = clone.groupUrl("/demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path.group(1), "/")
        self.assertEqual(path.group(2), "demo.foo.co.uk/bar/assets/images/menu.png")

        path = clone.groupUrl("demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path.group(1), None)
        self.assertEqual(path.group(2), "demo.foo.co.uk/bar/assets/images/menu.png")

        path = clone.groupUrl("./demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path.group(1), None)
        self.assertEqual(path.group(2), "./demo.foo.co.uk/bar/assets/images/menu.png")

    def test_getItem(self):
        #  import with // from an url
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/css", "//demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  absolute path import
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/css", "/bar/assets/images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  relative import from an url
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/css", "../images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  import from same path as the url
        item = clone.getItem("https://demo.foo.co.uk/bar/assets", "images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  import https
        item = clone.getItem("https://demo.foo.co.uk/bar/assets", "https://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  import http
        item = clone.getItem("https://demo.foo.co.uk/bar/assets", "http://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(item, "http://demo.foo.co.uk/bar/assets/images/menu.png")

        # ******* check for the same above but url ends with / ******* #

        #  import with // from an url
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/css/", "//demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  absolute path import
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/css/", "/bar/assets/images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  relative import from an url
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/css/", "../images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  import from same path as the url
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/", "images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  import https
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/", "https://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(item, "https://demo.foo.co.uk/bar/assets/images/menu.png")

        #  import http
        item = clone.getItem("https://demo.foo.co.uk/bar/assets/", "http://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(item, "http://demo.foo.co.uk/bar/assets/images/menu.png")

    def test_getDownloadPath(self):
        path = clone.getDownloadPath("https://demo.foo.co.uk/bar/assets/images/menu.png")
        self.assertEqual(path, "base_path/bar/assets/images/menu.png")

        path = clone.getDownloadPath("https://demo.foo.co.uk/bar/assets/images/menu.png?foo=bar")
        self.assertEqual(path, "base_path/bar/assets/images/menu.png")

        path = clone.getDownloadPath("https://demo.foo.co.uk/bar/assets/images/menu.png#top")
        self.assertEqual(path, "base_path/bar/assets/images/menu.png")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

