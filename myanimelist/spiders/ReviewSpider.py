import scrapy
from myanimelist.items import ReviewItem


class ReviewSpider(scrapy.Spider):
    name = 'ReviewSpider'
    allowed_domains = ['myanimelist.net']

    def start_requests(self):
        # กำหนดค่าเริ่มต้นสำหรับ start และ end limit
        start_page = int(getattr(self, 'start', 1))  # เริ่มต้นหน้าที่ 1
        end_page = int(getattr(self, 'end', 5))     # สิ้นสุดหน้าที่ 5

        # Loop ผ่านแต่ละหน้าที่กำหนด
        for page in range(start_page, end_page + 1):
            yield scrapy.Request(
                url=f'https://myanimelist.net/reviews.php?t=anime&p={page}',
                callback=self.parse
            )

    def parse(self, response):
        # ดึงข้อมูลรีวิวในแต่ละหน้า
        for review in response.css("div.borderDark"):
            review_link = review.css("div.clearfix a::attr(href)").get()
            if review_link:
                yield response.follow(review_link, self.parse_review)

    def parse_review(self, response):
        attr = {}
        attr['link'] = response.url
        attr['uid'] = response.url.split("id=")[1]

        # ดึงข้อมูล User Profile
        url_profile = response.css("td a[href*=profile] ::attr(href)").get()
        attr['profile'] = url_profile.split("/")[-1] if url_profile else "Unknown"

        # ดึงข้อความรีวิว
        attr['text'] = " ".join(response.css("div.textReadability ::text").getall()).strip()

        # ดึงคะแนน
        scores = response.css("div.textReadability td ::text").getall()
        scores_dict = dict(zip(scores[::2], scores[1::2]))  # สร้างคู่ key-value
        attr['scores'] = scores_dict
        attr['score'] = scores_dict.get('Overall', "Unknown")

        yield ReviewItem(**attr)
