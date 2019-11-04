import json
import base64
import scrapy
import tldextract
from scrapy import signals

from friedmansscraper.utils import *

ALL_FOUND_TWITTERS = "all found twitters"
popular_email_domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com", "aol.com", "mail.com", "msn.com",
                         "hotmail.com", " charter.net", "verizon.net", "alltel.net", "optimumonline.net", "new.rr.com",
                         "rr.com", "mchsi.com", "mediacomtoday.com", "frontier.com"]
ignore_links = {
    '/share', '/search', '/intent', '/', '/about', '/account', '/accounts', '/activity', '/all', '/announcements',
    '/anywhere', '/api_rules', '/api_terms', '/apirules', '/apps', '/auth', '/badges', '/blog', '/business', '/buttons',
    '/contacts', '/devices', '/direct_messages', '/download', '/downloads', '/edit_announcements', '/faq', '/favorites',
    '/find_sources', '/find_users', '/followers', '/following', '/friend_request', '/friendrequest',
    '/friends', '/goodies', '/help', '/home', '/im_account', '/inbox', '/invitations', '/invite', '/jobs', '/list',
    '/login', '/logo', '/logout', '/me', '/mentions', '/messages', '/mockview', '/newtwitter', '/notifications',
    '/nudge', '/oauth', '/phoenix_search', '/positions', '/privacy', '/public_timeline', '/related_tweets', '/replies',
    '/retweeted_of_mine', '/retweets', '/retweets_by_others', '/rules', '/saved_searches', '/search', '/sent',
    '/settings', '/share', '/signup', '/signin', '/similar_to', '/statistics', '/terms', '/tos', '/translate',
    '/trends', '/tweetbutton', '/twttr', '/update_discoverability', '/users', '/welcome', '/who_to_follow', '/widgets',
    '/zendesk_auth', '/media_signup', '/intent/tweet', '/intent/retweet', '/intent/like', '/messages/compose',
    '/intent/follow', '/intent/user'
}


class FriedmansSpider(scrapy.Spider):
    name = "twitter"
    data = None
    header = []
    result_file = "result.csv"
    current_row = ""
    all_twitter_links = set()
    user_name = []
    email_user_name = []
    index = 10
    requested_urls = set()
    depth = 5
    name_index = 1

    def __init__(self, data=None, index=10, depth=5, name_index=1, result_filename=None, **kwargs):
        super(FriedmansSpider, self).__init__(**kwargs)
        if not data:
            raise ValueError("%s must have a data" % type(self).__name__)
        if not result_filename:
            raise ValueError("%s must have a result file name" % type(self).__name__)
        self.data = json.loads(base64.b64decode(data))
        self.logger.info(self.data)
        self.name_index = int(name_index)
        self.user_name = user_name_to_list(self.data[self.name_index])
        if len(filter(validators.email, self.data)) > 0:
            self.email_user_name = email_user_name_to_list(filter(validators.email, self.data)[0])
        self.index = int(index)
        self.depth = int(depth)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FriedmansSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)
        twitter_links = self.all_twitter_links
        self.logger.info(twitter_links)
        while len(self.data) < self.index:
            self.data.append("")
        match_twitter = ["; ".join(twitter_links)]
        self.logger.debug("Name : {0} ; Name from e-mail : {1}".format(self.user_name, self.email_user_name))
        for tw_item in twitter_links:
            result = check_name_in_link(tw_item, self.user_name, self.email_user_name)
            if result:
                match_twitter += result
        self.data += match_twitter
        self.logger.debug("Row : {}".format(self.data))
        with open(self.result_file, 'a') as result_file:
            result_file.write(",".join(self.data) + "\n")

    def validate_absolute_links(self, root_url, link):
        return root_url in link \
               and link not in self.requested_urls \
               and ".pdf" not in link \
               and ".jpg" not in link \
               and ".png" not in link \
               and ".jpeg" not in link

    def validate_relative_links(self, root_url, link):
        return len(link) > 2 \
               and root_url + link not in self.requested_urls \
               and link[0] == "/" and link[1] != "/" \
               and ".pdf" not in link \
               and ".jpg" not in link \
               and ".png" not in link \
               and ".jpeg" not in link

    def parse(self, response, depth=1):
        self.logger.debug("! Parse callback for URL: {} !".format(response.request.url))
        self.logger.debug("Parse depth : {}".format(depth))
        all_links = response.xpath('//a/@href').extract()
        # self.logger.debug(all_links)
        o = urlparse(response.request.url)
        root_url = o.scheme + "://" + o.netloc
        if depth < self.depth:
            for link in all_links:
                if self.validate_absolute_links(root_url, link):
                    self.requested_urls.add(link)
                    yield scrapy.Request(url=link, callback=self.parse, cb_kwargs={"depth": depth + 1})
                elif self.validate_relative_links(root_url, link):
                    link = root_url + link
                    self.requested_urls.add(link)
                    yield scrapy.Request(url=link, callback=self.parse, cb_kwargs={"depth": depth + 1})
        all_links = filter(lambda x: "twitter" in x, all_links)
        self.logger.debug("All link candidates : {}".format(all_links))
        twitter_link_list = set()
        for link_candidate in all_links:
            twitter_link = check_is_twitter(link_candidate)
            self.logger.debug("Twitter link : {}".format(twitter_link))
            if twitter_link:
                twitter_link_list.add(twitter_link)
        self.logger.debug(twitter_link_list)
        self.all_twitter_links = self.all_twitter_links.union(twitter_link_list)
        self.logger.debug("Currently found twitter links : {}".format(list(self.all_twitter_links)))

    def start_requests(self):
        try:
            self.logger.info(self.data)
            urls = filter(validators.url, self.data)
            self.logger.info("!! urls {}".format(urls))
            try:
                email_domain_list = filter(validators.email, self.data)
                if len(email_domain_list) > 0:
                    email_domain = email_domain_list[0].split("@")[1]
                    if email_domain not in popular_email_domains:
                        url_obj = tldextract.extract(email_domain)
                        if url_obj.subdomain:
                            self.requested_urls.add("https://" + email_domain)
                            yield scrapy.Request(url="https://" + email_domain,
                                                 callback=self.parse, cb_kwargs={"depth": 1})
                            self.requested_urls.add("http://" + email_domain)
                            yield scrapy.Request(url="http://" + email_domain,
                                                 callback=self.parse, cb_kwargs={"depth": 1})
                        self.requested_urls.add("https://" + url_obj.domain + "." + url_obj.suffix)
                        yield scrapy.Request(url="https://" + url_obj.domain + "." + url_obj.suffix,
                                             callback=self.parse, cb_kwargs={"depth": 1})
                        self.requested_urls.add("http://" + url_obj.domain + "." + url_obj.suffix)
                        yield scrapy.Request(url="http://" + url_obj.domain + "." + url_obj.suffix,
                                             callback=self.parse, cb_kwargs={"depth": 1})

            except Exception, e:
                self.logger.exception(e.message)
            for url in urls:
                try:
                    if url not in self.requested_urls:
                        self.requested_urls.add(url)
                        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"depth": 1})
                    o = urlparse(url)
                    root_url = o.scheme + "://" + o.netloc
                    if root_url != url and root_url not in self.requested_urls:
                        self.requested_urls.add(root_url)
                        yield scrapy.Request(url=root_url, callback=self.parse, cb_kwargs={"depth": 1})
                except Exception, e:
                    self.logger.exception(e.message)
            self.logger.debug("! This is the end of the row !")
        except Exception, e:
            self.logger.exception(e.message)
