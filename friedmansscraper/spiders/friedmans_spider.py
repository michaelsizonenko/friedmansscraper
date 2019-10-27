import scrapy
import json
import validators
import base64
from urlparse import urlparse

from scrapy import signals

ALL_FOUND_TWITTERS = "all found twitters"
NAME_INDEX = 1
popular_email_domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com", "aol.com", "mail.com"]
ignore_links = ["https://www.twitter.com/home"]


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

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 10,
        'RETRY_ENABLED': False,
        'ROBOTSTXT_OBEY': False
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
        twitter_links = self.all_twitter_links
        self.logger.info(twitter_links)
        spider.logger.info('Spider closed: %s', spider.name)
        while len(self.data) < int(self.index):
            self.data.append("")
        with open(self.result_file, 'a') as result_file:
            new_column = " ".join(twitter_links)
            self.data.append(new_column)
            result_file.write(",".join(self.data) + "\n")

    def validate_absolute_links(self, root_url, link):
        return root_url in link \
               and link not in self.requested_urls \
               and ".pdf" not in link \
               and ".jpg" not in link \
               and ".jpeg" not in link

    def validate_relative_links(self, root_url, link):
        return len(link) > 2 \
               and root_url + link not in self.requested_urls \
               and link[0] == "/" and link[1] != "/" \
               and ".pdf" not in link \
               and ".jpg" not in link \
               and ".jpeg" not in link

    def parse(self, response, primary=False):
        self.logger.debug("! Parse callback for URL: {} !".format(response.request.url))
        self.logger.debug("Primary ? {}".format(primary))
        # self.all_twitter_links += filter(lambda x: "twitter" in x, response.xpath('//a/@href').extract())
        all_links = response.xpath('//a/@href').extract()
        self.logger.debug(all_links)
        o = urlparse(response.request.url)
        root_url = o.scheme + "://" + o.netloc
        if primary:
            for link in all_links:
                if self.validate_absolute_links(root_url, link):
                    self.requested_urls.add(link)
                    yield scrapy.Request(url=link, callback=self.parse, cb_kwargs={"primary": False})
                elif self.validate_relative_links(root_url, link):
                    link = root_url + link
                    self.requested_urls.add(link)
                    yield scrapy.Request(url=link, callback=self.parse, cb_kwargs={"primary": False})
        twitter_links = filter(lambda x: "twitter.com" in x, all_links)
        self.logger.debug(twitter_links)
        twitter_links = [x.split("?")[0] if "?" in x else x for x in twitter_links]
        self.logger.debug(twitter_links)
        twitter_links = filter(lambda x: x not in ignore_links, twitter_links)
        for link in twitter_links:
            if "/status/" in link:
                link = link.split("/status/")[0]
            self.all_twitter_links.add(link)
        self.logger.debug(self.all_twitter_links)

    def start_requests(self):
        try:
            self.logger.info(self.data)
            urls = filter(validators.url, self.data)
            self.logger.info("!! urls {}".format(urls))
            try:
                email_domain = filter(validators.email, self.data)[0].split("@")[1]
                if email_domain not in popular_email_domains and email_domain not in "\n".join(urls):
                    self.requested_urls.add("https://" + email_domain)
                    yield scrapy.Request(url="https://" + email_domain, callback=self.parse, cb_kwargs={"primary": True})
            except Exception, e:
                self.logger.exception(e.message)
            for url in urls:
                try:
                    if url not in self.requested_urls:
                        self.requested_urls.add(url)
                        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"primary": True})
                    o = urlparse(url)
                    root_url = o.scheme + "://" + o.netloc
                    if root_url != url and root_url not in self.requested_urls:
                        self.requested_urls.add(root_url)
                        yield scrapy.Request(url=root_url, callback=self.parse, cb_kwargs={"primary": True})
                except Exception, e:
                    self.logger.exception(e.message)
            self.logger.debug("! This is the end of the row !")
        except Exception, e:
            self.logger.exception(e.message)
