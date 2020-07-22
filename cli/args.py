import argparse
import csv
import os.path

from scrapy.crawler import CrawlerProcess

from amazonscraper.spiders import amazon_spider

ROOT_FOLDER = os.path.abspath(os.curdir)
PRODUCT_FOLDER = ROOT_FOLDER + '\\products'
# PRODUCT_FOLDER = '../products'
URL_INIT = 'https://www.amazon.it/gp/offer-listing/'


def get_args():
    parser = argparse.ArgumentParser(description='Amazon price scraper')
    parser.add_argument('-a', '--Add', type=str, metavar='', help='Add a new product')
    parser.add_argument('-s', '--Scrape', action='store_true', help='Start a new scrape cycle')
    return parser.parse_args()


def add(product_code):
    file_name = os.path.join(PRODUCT_FOLDER, product_code)

    if not os.path.exists(PRODUCT_FOLDER):
        os.makedirs(PRODUCT_FOLDER)

    if not os.path.isfile(file_name):
        with open(file_name, 'w', newline='') as file:
            file_writer = csv.writer(file, delimiter=',')
            file_writer.writerow(["time", "amazon", "amazon_warehouse", "new_ext", "used_ext"])
        print('New product added: ' + product_code)


def scrape():
    process = CrawlerProcess()
    process.crawl(amazon_spider)
    process.start()


if __name__ == "__main__":
    args = get_args()

    if args.Add:
        add(args.Add)

    if args.Scrape:
        scrape()
