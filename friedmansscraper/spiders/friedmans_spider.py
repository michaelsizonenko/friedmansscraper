import scrapy
import csv
import validators


class FriedmansSpider(scrapy.Spider):
    name = "twitter"
    filename = None

    def __init__(self, filename=None, **kwargs):
        super(FriedmansSpider, self).__init__(**kwargs)
        if not filename:
            raise ValueError("%s must have a filename" % type(self).__name__)
        self.filename = filename

    def parse(self, response):
        links = response.xpath('//a/@href').extract()
        for link in links:
            if "twitter" in link:
                print("!! twitter link found !!")
                print(link)

    def start_requests(self):
        name_index = 0
        email_index = 1
        urls_index = 2

        with open(self.filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                meta = {
                    "name": row[name_index],
                    "email": row[email_index]
                }
                urls = filter(validators.url, row[urls_index:])
                for url in urls:
                    yield scrapy.Request(url=url, callback=self.parse, meta=meta)
