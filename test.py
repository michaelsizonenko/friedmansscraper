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
        test_result = check_is_twitter("https://twitter.com/hashtag/winter")
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
        test_result = check_is_twitter(u'https://twitter.com/nbcolympics/status/1190259907129425920')
        self.assertEqual('https://twitter.com/nbcolympics', test_result)

    def test_name_in_twitter_link(self):
        with self.assertRaises(TypeError):
            email_user_name_to_list()
        with self.assertRaises(TypeError):
            email_user_name_to_list("some string")
        test_result = email_user_name_to_list("mcares@ci.missoula.mt.us")
        self.assertEqual(test_result, {"mcares"})
        test_result = email_user_name_to_list("shawn.steffen@griggscountynd.gov")
        self.assertEqual(test_result, {"shawn", "steffen"})
        test_result = email_user_name_to_list("Sharon_h@co.redwood.mn.us")
        self.assertEqual(test_result, {"sharon"})
        test_result = email_user_name_to_list("Sharon.Middleton@baltimorecity.gov")
        self.assertEqual(test_result, {"sharon", "middleton"})
        test_result = email_user_name_to_list("sdowner55@gmail.com")
        self.assertEqual(test_result, {"sdowner"})
        test_result = email_user_name_to_list("thomas_thrush@lasallecounty.org")
        self.assertEqual(test_result, {"thomas", "thrush"})
        test_result = email_user_name_to_list("tmac_911@hotmail.com")
        self.assertEqual(test_result, {"tmac"})
        test_result = email_user_name_to_list("TownManager-Selectmen@townhall.plymouth.ma.us")
        self.assertEqual(test_result, {"townmanager", "selectmen"})
        test_result = email_user_name_to_list("w.tallman5909@comcast.net")
        self.assertEqual(test_result, {"tallman"})

    def test_extract_name(self):
        with self.assertRaises(TypeError):
            user_name_to_list()
        with self.assertRaises(TypeError):
            user_name_to_list(123)
        type_result = user_name_to_list("Bill Tallman")
        self.assertEqual(type_result, {"bill", "tallman"})
        type_result = user_name_to_list(u"Bill Tallman")
        self.assertEqual(type_result, {"bill", "tallman"})
        type_result = user_name_to_list(u"W. Davis Jr.")
        self.assertEqual(type_result, {"davis"})
        type_result = user_name_to_list("Bill Lockett Sr.")
        self.assertEqual(type_result, {"bill", "lockett"})
        type_result = user_name_to_list("Mary Chambers' Biography")
        self.assertEqual(type_result, {"mary", "chambers"})
        type_result = user_name_to_list("Commissioner Stephen Kelley - Biography - Vote Smart")
        self.assertEqual(type_result, {"stephen", "kelley"})
        type_result = user_name_to_list("Fred Thomas' Biography")
        self.assertEqual(type_result, {"fred", "thomas"})
        type_result = user_name_to_list("Scheketa Hart-Burns' Biography")
        self.assertEqual(type_result, {"scheketa", "hart-burns"})

    def test_extract_name_from_email(self):
        with self.assertRaises(TypeError):
            check_name_in_link()
        with self.assertRaises(TypeError):
            check_name_in_link(123)
        with self.assertRaises(TypeError):
            check_name_in_link(123, 456, 789)
        with self.assertRaises(TypeError):
            check_name_in_link("some string", {}, {})
        self.assertIsNone(check_name_in_link("http://twitter.com/apple", {"david", "williams"}, {"dave"}))
        test_result = check_name_in_link("http://twitter.com/davidwilliams", {"david", "williams"}, {"dave", "williams"})
        self.assertEqual(test_result, ["http://twitter.com/davidwilliams", "True", "True"])
        test_result = check_name_in_link("http://twitter.com/dave", {"david", "williams"}, {"dave", "williams"})
        self.assertEqual(test_result, ["http://twitter.com/dave", "True", "False"])
        for x in ["https://twitter.com/pftpm", "https://twitter.com/topgunxv", "https://twitter.com/unistudios",
                  "https://twitter.com/nascar", "https://twitter.com/nbcsports", "https://twitter.com/xfinity",
                  "https://twitter.com/leedixon2", "https://twitter.com/xfinityracing",
                  "https://twitter.com/universalorl", "https://twitter.com/nascaronnbc",
                  "https://twitter.com/nmlegislature", "https://twitter.com/harrietfilm",
                  "https://twitter.com/lifeatsky/", "https://twitter.com/lifeatsky",
                  "https://twitter.com/focusfeatures", "https://twitter.com/comcasttechsoln",
                  "https://twitter.com/raecomm", "https://twitter.com/nbcsportspr",
                  "https://twitter.com/comcastcareers", "https://twitter.com/easportsfifa",
                  "https://twitter.com/workatnbcu", "https://twitter.com/arlowhite",
                  "https://twitter.com/itsskitime", "https://twitter.com/comcast",
                  "https://twitter.com/profootballtalk", "https://twitter.com/comcastcares"]:
            self.assertIsNone(check_name_in_link(x, {"bill", "tallman"}, {"w", "tallman"}))


if __name__ == "__main__":
    unittest.main()
