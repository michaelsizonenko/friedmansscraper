import scrapy
import json
import validators
import base64
from tempfile import NamedTemporaryFile

from scrapy import signals

ALL_FOUND_TWITTERS = "all found twitters"


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
            print(new_column)
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
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
            self.logger.info("! This is the end !")
        except Exception, e:
            self.logger.exception(e.message)
