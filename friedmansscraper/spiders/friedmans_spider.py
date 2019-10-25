import scrapy
import json
import validators
import base64
from urlparse import urlparse

from scrapy import signals

ALL_FOUND_TWITTERS = "all found twitters"

popular_email_domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com", "aol.com", "mail.com"]

class FriedmansSpider(scrapy.Spider):
    name = "twitter"
    data = None
    header = []
    result_file = "result.csv"
    result_index = 0
    current_row = ""
    all_twitter_links = []

    def __init__(self, data=None, **kwargs):
        super(FriedmansSpider, self).__init__(**kwargs)
        if not data:
            raise ValueError("%s must have a data" % type(self).__name__)
        self.data = json.loads(base64.b64decode(data))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FriedmansSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        twitter_links = set(self.all_twitter_links)
        self.logger.info(twitter_links)
        spider.logger.info('Spider closed: %s', spider.name)
        with open(self.result_file, 'a') as result_file:
            new_column = " ".join(self.all_twitter_links)
            self.logger.info(new_column)
            self.data.append(new_column)
            result_file.write(",".join(self.data) + "\n")

    def parse(self, response):
        self.logger.info("! Parse callback !")
        self.all_twitter_links += filter(lambda x: "twitter" in x, response.xpath('//a/@href').extract())
        self.logger.info(self.all_twitter_links)

    def start_requests(self):
        try:
            self.logger.info(self.data)
            urls = filter(validators.url, self.data)
            self.logger.info("!! urls {}".format(urls))
            email_domain = self.data[1].split("@")[1]
            self.logger.info(email_domain)
            if email_domain not in popular_email_domains and email_domain not in "\n".join(urls):
                yield scrapy.Request(url=email_domain, callback=self.parse)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
                o = urlparse(url)
                root_url = o.scheme + "://" + o.netloc
                if root_url != url:
                    yield scrapy.Request(url=root_url, callback=self.parse)
            self.logger.info("! This is the end !")
        except Exception, e:
            self.logger.exception(e.message)
