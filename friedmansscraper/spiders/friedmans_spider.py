import scrapy
import json
import validators
import base64
from urlparse import urlparse

from scrapy import signals

ALL_FOUND_TWITTERS = "all found twitters"
NAME_INDEX = 1
popular_email_domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com", "aol.com", "mail.com"]
exclude_twitter_links = ["https://www.twitter.com/home"]


class FriedmansSpider(scrapy.Spider):
    name = "twitter"
    data = None
    header = []
    result_file = "result.csv"
    current_row = ""
    all_twitter_links = []
    user_name = []
    email_user_name = []
    index = 10

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 10,
        'RETRY_ENABLED': False
    }

    def __init__(self, data=None, index=10, **kwargs):
        super(FriedmansSpider, self).__init__(**kwargs)
        if not data:
            raise ValueError("%s must have a data" % type(self).__name__)
        self.data = json.loads(base64.b64decode(data))
        self.logger.info(self.data)
        self.user_name = self.user_name_to_list(self.data[NAME_INDEX])
        self.email_user_name = self.email_user_name_to_list(filter(validators.email, self.data)[0])
        self.index = index

    def user_name_to_list(self, user_name):
        return user_name.split(" ")

    def email_user_name_to_list(self, email):
        user_name = email.split("@")[0]
        user_name = user_name.replace("_", " ").replace(".", " ")
        return self.user_name_to_list(user_name)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FriedmansSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        twitter_links = set(self.all_twitter_links)
        self.logger.info(twitter_links)
        spider.logger.info('Spider closed: %s', spider.name)
        while len(self.data) < int(self.index):
            self.data.append("")
        with open(self.result_file, 'a') as result_file:
            new_column = " ".join(twitter_links)
            self.data.append(new_column)
            result_file.write(",".join(self.data) + "\n")

    def parse(self, response):
        self.logger.info("! Parse callback !")
        # self.all_twitter_links += filter(lambda x: "twitter" in x, response.xpath('//a/@href').extract())
        twitter_links = filter(lambda x: "twitter.com" in x and x not in exclude_twitter_links, response.xpath('//a/@href').extract())
        twitter_links = [x.split("?")[0] if "?" in x else x for x in twitter_links]
        self.all_twitter_links = twitter_links
        self.logger.info(self.all_twitter_links)

    def start_requests(self):
        try:
            self.logger.info(self.data)
            urls = filter(validators.url, self.data)
            self.logger.info("!! urls {}".format(urls))
            try:
                email_domain = filter(validators.email, self.data)[0].split("@")[1]
                if email_domain not in popular_email_domains and email_domain not in "\n".join(urls):
                    yield scrapy.Request(url="https://" + email_domain, callback=self.parse)
            except Exception, e:
                self.logger.exception(e.message)
            for url in urls:
                try:
                    yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                    o = urlparse(url)
                    root_url = o.scheme + "://" + o.netloc
                    if root_url != url:
                        yield scrapy.Request(url=root_url, callback=self.parse, dont_filter=True)
                except Exception, e:
                    self.logger.exception(e.message)
            self.logger.info("! This is the end !")
        except Exception, e:
            self.logger.exception(e.message)
