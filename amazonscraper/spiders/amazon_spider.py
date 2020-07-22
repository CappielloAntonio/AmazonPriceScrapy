import os
import re
from datetime import datetime

import scrapy

from amazonscraper.items import AmazonScraperItem
from cli import args


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    start_urls = ['https://www.amazon.it/gp/offer-listing/' + file for file in os.listdir(args.PRODUCT_FOLDER)]

    def parse(self, response):
        item = AmazonScraperItem()
        time = datetime.now()
        code = response.request.url.split('/')[-1]

        products = response.css('.olpOffer')
        for product in products:
            product_price = product.css('.olpOfferPrice::text').extract_first()
            product_condition = product.css('.olpCondition::text').extract_first()
            product_seller = product.css('.a-text-bold a').css("::text").extract_first() or product.css(
                'img::attr(alt)').extract_first()

            raw_price = re.sub(r'\s+', ' ', product_price.strip())
            str_price = re.search("([0-9]+[,.]+[0-9]+)", raw_price).group().replace(',', '.')
            flt_price = float(str_price)

            item['time'] = time.strftime("%Y/%m/%d %H:%M")
            item['code'] = code
            item['product_price'] = flt_price
            item['product_condition'] = re.sub(r'\s+', ' ', product_condition.strip())
            item['product_seller'] = re.sub(r'\s+', ' ', product_seller.strip())

            yield item
