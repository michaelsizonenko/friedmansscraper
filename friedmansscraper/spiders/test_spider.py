import scrapy


class TwitterSpider(scrapy.Spider):
    name = 'test_twitter'
    start_urls = ['https://blog.scrapinghub.com']

    def parse(self, response):
        all_links = response.xpath('//a/@href').extract()
        self.logger.debug(all_links)