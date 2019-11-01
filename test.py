import unittest
from friedmansscraper.spiders.friedmans_spider import *
from friedmansscraper.utils import *
from urlparse import urljoin


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

    def test_is_twitter_account(self):
        with self.assertRaises(TypeError):
            check_is_twitter()
        with self.assertRaises(TypeError):
            check_is_twitter(None)
        with self.assertRaises(Exception):
            check_is_twitter("some string")
        self.assertIsNone(check_is_twitter("https://google.com"))
        inappropriate_url_list = [
            "https://twitter.com",
            "https://twitter.com/",
            "http://twitter.com",
            "http://twitter.com/",
            "https://www.twitter.com",
            "https://www.twitter.com/",
            "http://mobile.twitter.com",
            "http://mobile.twitter.com/"
        ]
        for inappropriate_url in inappropriate_url_list:
            test_result = check_is_twitter(inappropriate_url)
            self.assertEqual(test_result, None, "None expected. {} found".format(test_result))
            for ignore_link_path in IGNORE_LINK_PATHS:
                ignore_link = urljoin(inappropriate_url, ignore_link_path)
                self.assertIsNone(check_is_twitter(ignore_link))
        test_result = check_is_twitter("http://twitter.com/intent/tweet")
        self.assertIsNone(test_result)
        test_result = check_is_twitter("https://twitter.com/share")
        self.assertIsNone(test_result)
        test_result = check_is_twitter("https://twitter.com/CityofKissimmee")
        self.assertEqual('https://twitter.com/cityofkissimmee', test_result)
        test_result = check_is_twitter("http://www.twitter.com/nbpio")
        self.assertEqual('https://twitter.com/nbpio', test_result)
        test_result = check_is_twitter("http://twitter.com/#!/champaigncity")
        self.assertEqual('https://twitter.com/champaigncity', test_result)
        test_result = check_is_twitter(u"https://twitter.com/C_V_C_C")
        self.assertEqual('https://twitter.com/c_v_c_c', test_result)
        test_result = check_is_twitter(u'http://twitter.com/alabamacounties')
        self.assertEqual('https://twitter.com/alabamacounties', test_result)






if __name__ == "__main__":
    unittest.main()
