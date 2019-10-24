import scrapy
import csv
import validators


class FriedmansSpider(scrapy.Spider):
    name = "twitter"

    def parse(self, response):
        print("!!! Parse callback !!!")
        print(response)

    def start_requests(self):
        name_index = 0
        email_index = 1
        urls_index = 2

        with open('/home/dethline/software/projects/friedmansscraper/test.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                print("!! Row of the file {}".format(row))
                meta = {
                    "name": row[name_index],
                    "email": row[email_index]
                }
                urls = filter(validators.url, row[urls_index:])
                for url in urls:
                    yield scrapy.Request(url=url, callback=self.parse, meta=meta)
