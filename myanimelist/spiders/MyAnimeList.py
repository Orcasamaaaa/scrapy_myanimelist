# -*- coding: utf-8 -*-
import scrapy
import numpy as np
from myanimelist.items import AnimeItem, ReviewItem, ProfileItem

# https://myanimelist.net/topanime.php?limit=<limit>
#
# scrapy runspider myanimelist/spiders/MyAnimeList.py
# -a start_limit=<start_limit>
# -a end_limit=<end_limit>
# -s MONGODB_URL=<mongo_uri>
#
class MyAnimeListSpider(scrapy.Spider):
    name = 'MyAnimeList'
    allowed_domains = ['myanimelist.net']

    def start_requests(self):
        yield scrapy.Request('https://myanimelist.net/topanime.php?limit=%s' % self.start_limit) #16300

    # https://myanimelist.net/topanime.php
    def parse(self, response):
      self.logger.info('Parse function called on %s', response.url)

      limit = response.url.split("limit=")[1]
      if int(limit) > int(self.end_limit):
        return

      for rank in response.css(".ranking-list"):
        link    = rank.css("td.title a::attr(href)").extract_first()

        yield response.follow(link, self.parse_anime)

      next_page = response.css("div.pagination a.next ::attr(href)").extract_first()
      if next_page is not None:
          yield response.follow("{}{}".format(response.url.split("?")[0], next_page), self.parse)

    # https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood
    def parse_anime(self, response):
        attr = {}
        attr['link'] = response.url
        attr['uid'] = self._extract_anime_uid(response.url)

        # ดึงข้อมูล Title
        attr['title'] = response.css("h1.title-name.h1_bold_none strong::text").get(default="Unknown").strip()

        # ดึงข้อมูล Synopsis
        attr['synopsis'] = " ".join(response.xpath("//p[@itemprop='description']/text()").getall()).strip()

        # ดึงข้อมูลอื่น ๆ
        attr['score'] = response.css("div.score ::text").get()
        attr['ranked'] = response.css("span.ranked strong ::text").get()
        attr['popularity'] = response.css("span.popularity strong ::text").get()
        attr['members'] = response.css("span.members strong ::text").get()
        attr['genre'] = response.css("div span[itemprop='genre'] ::text").getall()

        # ดึงข้อมูล Demographic
        attr['demographic'] = response.xpath("//span[text()='Demographic:']/following-sibling::a/text()").get(
            default="Unknown").strip()

        # ดึง URL รูปภาพจาก data-src หรือ fallback เป็น src
        attr['img_url'] = response.css("td.borderClass div.leftside img::attr(data-src)").get() or \
                          response.css("td.borderClass div.leftside img::attr(src)").get()

        # ดึงข้อมูล Episodes
        attr['episodes'] = response.xpath("//span[text()='Episodes:']/following-sibling::text()").get(
            default="Unknown").strip()

        # ดึงข้อมูล Aired
        attr['aired'] = response.xpath("//span[text()='Aired:']/following-sibling::text()").get(
            default="Unknown").strip()

        # ตรวจสอบว่าข้อมูลที่ดึงมาว่างหรือไม่
        if not attr['title']:
            self.logger.warning(f"Title information missing at {response.url}")
        if not attr['img_url']:
            self.logger.warning(f"Image URL missing for {attr['title']} at {response.url}")

        # ส่งข้อมูลออกเป็น AnimeItem
        yield AnimeItem(**attr)


    def parse_list_review(self, response):
      p = response.url.split("p=")[1]

      reviews = response.css("div.borderDark")
      for review in reviews:
        link = review.css("div.clearfix a::attr(href)").extract_first()
        yield response.follow(link, self.parse_review)

      # None, First Page and not last page
      next_page = response.css("div.mt4 a::attr(href)").extract()
      if next_page is not None and len(reviews) > 0 and len(next_page) > 0 and (p == '1' or len(next_page) > 1):
        next_page = next_page[0] if p == '1' else next_page[1]
        yield response.follow(next_page, self.parse_list_review)

    # https://myanimelist.net/reviews.php?id=<uid>
    def parse_review(self, response):
      attr   = {}
      attr['link']      = response.url
      attr['uid']       = response.url.split("id=")[1]
      attr['anime_uid'] = self._extract_anime_uid(response.css("a.hoverinfo_trigger ::attr(href)").extract_first())
      attr['uid']       = response.url.split("id=")[1]

      url_profile       = response.css("td a[href*=profile] ::attr(href)").extract_first()
      attr['profile']   = url_profile.split("/")[-1]
      attr['text']      = " ".join(response.css("div.textReadability ::text").extract())

      scores            =  np.array(response.css("div.textReadability td ::text").extract())
      scores = dict(zip(scores[[i for i in range(12) if (i%2) == 0]],
                          scores[[i for i in range(12) if (i%2) == 1]] ))
      attr['scores']    = scores
      attr['score']     = scores['Overall']

      # /review
      yield ReviewItem(**attr)

      # /profile
      yield response.follow(url_profile, self.parse_profile)

    # https://myanimelist.net/profile/<uid>
    def parse_profile(self, response):
      attr   = {}
      attr['link']     = response.url
      attr['profile']  = response.url.split("/")[-1]

      url_favorites = response.css("ul.favorites-list.anime li div.data a ::attr(href)").extract()
      attr['favorites'] = [self._extract_anime_uid(url) for url in url_favorites]

      user_status   = response.css("div.user-profile ul.user-status li.clearfix ::text").extract()
      user_status   = self._list2dict(user_status)

      attr['gender']   = user_status['Gender'] if 'Gender' in user_status else ''
      attr['birthday'] = user_status['Birthday'] if 'Birthday' in user_status else ''

      yield ProfileItem(**attr)

    def _extract_anime_uid(self, url):
      return url.split("/")[4]

    def _list2dict(self, attrs):
      attrs = np.array(attrs)
      attrs = dict(zip(attrs[[i for i in range(len(attrs)) if (i%2) == 0]],
                          attrs[[i for i in range(len(attrs)) if (i%2) == 1]] ))
      return attrs
