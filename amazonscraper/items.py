# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonScraperItem(scrapy.Item):
    time = scrapy.Field()
    code = scrapy.Field()
    product_price = scrapy.Field()
    product_condition = scrapy.Field()
    product_seller = scrapy.Field()
