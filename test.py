import unittest
from friedmansscraper.spiders.friedmans_spider import *
from friedmansscraper.utils import *


class TestParser(unittest.TestCase):

    def test_multiple_links(self):
        with self.assertRaises(TypeError):
            get_urls_from_the_row(None)
        with self.assertRaises(TypeError):
            get_urls_from_the_row("somestring")
        with self.assertRaises(TypeError):
            get_urls_from_the_row({})
        test_result = get_urls_from_the_row(list("some string"))
        self.assertEqual(test_result, set(), "Error. Expected empty list. Found {}".format(test_result))
        test_result = get_urls_from_the_row(set("some_string"))
        self.assertEqual(test_result, set(), "Error. Expected empty list. Found {}".format(test_result))
        test_result = get_urls_from_the_row(tuple("some_string"))
        self.assertEqual(test_result, set(), "Error. Expected empty list. Found {}".format(test_result))
        test_result = get_urls_from_the_row(["https://google.com", "some string google.com"])
        self.assertEqual(test_result, {"https://google.com"}, "Found {}".format(test_result))
        test_result = get_urls_from_the_row(["https://google.com", "some string google.com", "https://google.com"])
        self.assertEqual(test_result, {"https://google.com"})
        test_result = get_urls_from_the_row(
            ["http://www.votenewt.com | http://house.gov/newt.html | http://www.newtnews.com", "some string"])
        self.assertEqual(test_result,
                         {"http://www.votenewt.com", "http://house.gov/newt.html", "http://www.newtnews.com"})
        test_result = get_urls_from_the_row(
            ["http://www.votenewt.com | http://house.gov/newt.html | http://www.newtnews.com", "some string",
             "https://google.com"])
        self.assertEqual(test_result,
                         {"http://www.votenewt.com", "http://house.gov/newt.html", "http://www.newtnews.com",
                          "https://google.com"})
        test_result = get_urls_from_the_row(["http://www.northamptoncounty.org/northampton/cwp/view.asp?a=1518&Q=620119&northamptonNav=|34398|&northamptonNav_GID=1977"])
        self.assertEqual(test_result, {"http://www.northamptoncounty.org/northampton/cwp/view.asp?a=1518&Q=620119&northamptonNav=|34398|&northamptonNav_GID=1977"})


if __name__ == "__main__":
    unittest.main()
