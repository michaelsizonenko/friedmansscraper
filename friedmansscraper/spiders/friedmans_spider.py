import scrapy
import json
import validators
import base64
from tempfile import NamedTemporaryFile

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

    def parse(self, response):
        print("!!!!! parse !!!!")
        self.all_twitter_links += filter(lambda x: "twitter" in x, response.xpath('//a/@href').extract())
        print(self.all_twitter_links)

    def start_requests(self):
        try:
            print("!!!!!!!!!!")
            print(self.data)
            urls = filter(validators.url, self.data)
            print("!! urls {}".format(urls))
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
                # with open(self.result_file, 'a') as result_file:
                #     new_column = " ".join(self.all_twitter_links)
                #     print("!!!!!")
                #     print(new_column)
                #     row.append(new_column)
                #     result_file.write(",".join(row) + "\n")
                # self.all_twitter_links = []
            print("! This is the end !")
        except Exception, e:
            print(e)
