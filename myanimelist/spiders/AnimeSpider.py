# -*- coding: utf-8 -*-
import scrapy
import numpy as np
from myanimelist.items import AnimeItem

class AnimeSpider(scrapy.Spider):
    name = 'AnimeSpider'
    allowed_domains = ['myanimelist.net']

    # กำหนดค่าเริ่มต้นของ start_limit และ end_limit
    def __init__(self, start_limit=0, end_limit=1000, *args, **kwargs):
        super(AnimeSpider, self).__init__(*args, **kwargs)
        self.start_limit = int(start_limit)
        self.end_limit = int(end_limit)

    def start_requests(self):
        url = f'https://myanimelist.net/topanime.php?limit={self.start_limit}'
        yield scrapy.Request(url, self.parse)

    # https://myanimelist.net/topanime.php
    def parse(self, response):
        self.logger.info('Parse function called on %s', response.url)

        # ตรวจสอบ limit ปัจจุบัน
        limit = int(response.url.split("limit=")[1])
        if limit > self.end_limit:
            self.logger.info("Reached the end limit. Stopping scrape.")
            return

        # ดึงลิงก์รายการอนิเมะ
        for rank in response.css(".ranking-list"):
            link = rank.css("td.title a::attr(href)").get()
            if link:
                yield response.follow(link, self.parse_anime)

        # ไปยังหน้าถัดไป
        next_page = response.css("div.pagination a.next ::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, self.parse)

    # https://myanimelist.net/anime/<uid>/<title>
    def parse_anime(self, response):
        attr = {}
        attr['link'] = response.url
        attr['uid'] = self._extract_anime_uid(response.url)

        # ดึงข้อมูลต่างๆ
        attr['title'] = self.validate_attr(
            response.css("h1.title-name.h1_bold_none strong::text").get(), default="Unknown"
        )
        attr['synopsis'] = self.validate_attr(
            " ".join(response.xpath("//p[@itemprop='description']/text()").getall()), default="No synopsis available"
        )
        attr['score'] = response.css("div.score ::text").get()
        attr['ranked'] = response.css("span.ranked strong ::text").get()
        attr['popularity'] = response.css("span.popularity strong ::text").get()
        attr['members'] = response.css("span.members strong ::text").get()
        attr['genre'] = response.css("div span[itemprop='genre'] ::text").getall()
        attr['demographic'] = self.validate_attr(
            response.xpath("//span[text()='Demographic:']/following-sibling::a/text()").get(), default="Unknown"
        )
        attr['img_url'] = (
            response.css("td.borderClass div.leftside img::attr(data-src)").get() or
            response.css("td.borderClass div.leftside img::attr(src)").get()
        )
        attr['episodes'] = self.validate_attr(
            response.xpath("//span[text()='Episodes:']/following-sibling::text()").get(), default="Unknown"
        )
        attr['aired'] = self.validate_attr(
            response.xpath("//span[text()='Aired:']/following-sibling::text()").get(), default="Unknown"
        )

        # ตรวจสอบและแจ้งเตือนข้อมูลที่ขาดหาย
        if not attr['title'] or attr['title'] == "Unknown":
            self.logger.warning(f"Missing title information at {response.url}")
        if not attr['img_url']:
            self.logger.warning(f"Missing image URL for {attr['title']} at {response.url}")

        # ส่งข้อมูลออกเป็น AnimeItem
        yield AnimeItem(**attr)

    # ฟังก์ชันตรวจสอบข้อมูล
    def validate_attr(self, value, data_type=str, default=None):
        try:
            if value is None or value.strip() == "":
                return default
            if data_type == float and value == "N/A":
                return np.nan
            return data_type(value.strip())
        except (ValueError, TypeError):
            return default

    def _extract_anime_uid(self, url):
        return url.split("/")[4]
