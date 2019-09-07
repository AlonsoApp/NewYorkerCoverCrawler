#!/usr/bin/env python
import time
import scrapy
from datetime import datetime, timedelta
from requests import get

FAILED_LOG = 'failed.txt'

URL_BASE = "https://www.newyorker.com"
IMG_PATH = "./covers/"

BUTTON_SELECTOR = '.Button__button___2vDCa'
DATALINK_SELECTOR = 'button::attr(data-link)'
COVER_DIV = '.MagazineCover__cover___2bDZf'
IMG_SELECTOR = '.component-responsive-image'
MEDIA_SELECTOR = 'source::attr(media)'
SRCSET_SELECTOR = 'source::attr(srcset)'

IMG_FORMAT = '.jpg'


class NewYorkerSpider(scrapy.Spider):
    name = "ny_spider"
    next_media = "/magazine/1925/02/21"
    start_urls = [str(URL_BASE + next_media)]

    def parse(self, response):
        try:
            button_next = response.css(BUTTON_SELECTOR)[1]
            next_media = button_next.css(DATALINK_SELECTOR).extract_first()

            cover_div = response.css(COVER_DIV)[0]

            source = cover_div.css(IMG_SELECTOR)[0]

            media = source.css(MEDIA_SELECTOR).extract_first()
            src_img = source.css(SRCSET_SELECTOR).extract_first()
            yield {
                'next_media': next_media,
                'media': media,
                'src_img': src_img,
            }
            img_url = src_img.split(' ')[1]
            img_name = self.build_img_file_name(response.request.url)
            self.download(img_url, str(IMG_PATH+img_name))

            if next_media != '':
                time.sleep(1)
                yield response.follow(str(URL_BASE + next_media), self.parse)
        except:
            self.file_print(response.request.url)
            yield response.follow(self.guess_next_url(response.request.url), self.parse)

    # Given the current url (which doesn't have next btn) tries to guess a url of the date of the current site +7 days
    def guess_next_url(self, url):
        old_year, old_month, old_day = self.extract_date(url)
        old_date = str(old_year + "/" + old_month + "/" + old_day)
        date_1 = datetime.strptime(old_date, "%Y/%m/%d")
        end_date = date_1 + timedelta(days=7)
        new_date = end_date.strftime("%Y/%m/%d")
        return url.replace(old_date, new_date)

    def build_img_file_name(self, url):
        year, month, day = self.extract_date(url)
        return str(year + "-" + month + "-" + day + IMG_FORMAT)

    @staticmethod
    def extract_date(url):
        year = url.split('/')[-3]
        month = url.split('/')[-2]
        day = url.split('/')[-1]
        return year, month, day

    @staticmethod
    def download(url, file_name):
        # open in binary mode
        with open(file_name, "wb") as file:
            # get request
            response = get(url)
            # write to file
            file.write(response.content)

    @staticmethod
    def file_print(output):
        with open(FAILED_LOG, "a") as f:
            f.write("{}\n".format(output))