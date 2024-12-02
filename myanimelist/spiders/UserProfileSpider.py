import scrapy
from myanimelist.items import ProfileItem
import json

class UserProfileSpider(scrapy.Spider):
    name = 'UserProfileSpider'
    allowed_domains = ['myanimelist.net']

    def __init__(self, start_limit=0, end_limit=100000, *args, **kwargs):
        super(UserProfileSpider, self).__init__(*args, **kwargs)
        self.start_limit = int(start_limit)  # limit เริ่มต้น
        self.end_limit = int(end_limit)  # limit สุดท้าย
        self.seen_usernames = set()  # เก็บชื่อผู้ใช้ที่เคยบันทึกไปแล้ว
        self.profile_count = 0  # ตัวนับจำนวนโปรไฟล์ที่ถูกดึงออกมา
        self.profiles_data = []  # เก็บข้อมูลโปรไฟล์ที่ถูก scrape
        self.current_page = self.start_limit  # ตัวแปรที่ใช้สำหรับคำนวณหน้า (0, 20, 40, ...)

    def start_requests(self):
        # เริ่มต้นที่หน้าแรกของรายการ
        url = f'https://myanimelist.net/users.php?cat=user&q=&show={self.current_page}'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        self.logger.info('Parsing page: %s', response.url)

        # ดึงลิงก์โปรไฟล์จากหน้า
        profile_links = response.css("a[href^='/profile/']::attr(href)").extract()

        if not profile_links:
            self.logger.warning("No profile links found on this page.")

        for profile_link in profile_links:
            self.logger.info(f"Found profile link: {profile_link}")
            yield response.follow(profile_link, self.parse_profile)

        # ตรวจสอบ limit ปัจจุบัน
        if self.profile_count >= self.end_limit:
            self.logger.info("Reached the end limit. Stopping scrape.")
            self.save_to_json()  # บันทึกข้อมูลเมื่อถึง limit
            return

        # เพิ่ม page offset ทีละ 20 เพื่อขอหน้าใหม่
        self.current_page += 20  # เพิ่มทีละ 20

        # ถ้าหน้ายังไม่ถึง limit และมีโปรไฟล์ให้ดึง ก็ให้ไปหน้าถัดไป
        if self.profile_count < self.end_limit:
            next_page_url = f'https://myanimelist.net/users.php?cat=user&q=&show={self.current_page}'
            self.logger.info(f"Requesting next page: {next_page_url}")
            yield scrapy.Request(next_page_url, self.parse)

    def parse_profile(self, response):
        attr = {}
        attr['profile_link'] = response.url
        attr['username'] = response.url.split("/")[-1]  # ดึงชื่อผู้ใช้จาก URL

        # เช็คว่าชื่อผู้ใช้ซ้ำหรือยัง
        if attr['username'] in self.seen_usernames:
            self.logger.info(f"Skipping duplicate profile: {attr['username']}")
            return  # ถ้าซ้ำก็ข้ามไปไม่ต้องบันทึก

        # ถ้าไม่ซ้ำ เพิ่มชื่อผู้ใช้ลงใน set
        self.seen_usernames.add(attr['username'])

        # ดึงข้อมูลโปรไฟล์ เช่น เพศ วันเกิด
        user_status = response.css("div.user-profile ul.user-status li.clearfix span::text").extract()
        user_status = self._list2dict(user_status)

        # กำหนดค่าเริ่มต้นถ้าไม่มีข้อมูล
        attr['gender'] = user_status.get('Gender', '')  # ใช้ค่าว่างถ้าไม่มีข้อมูล
        attr['birthday'] = user_status.get('Birthday', '')  # ใช้ค่าว่างถ้าไม่มีข้อมูล

        # ดึงข้อมูลรายการอนิเมะโปรด (favorites) โดยใช้ XPath
        url_favorites = response.xpath('//*[@id="anime_favorites"]//a[contains(@href, "/anime/")]/@href').extract()
        # ถ้ามี favorites ให้ดึง UID ของอนิเมะ
        attr['favorites'] = [self._extract_anime_uid(url) for url in url_favorites] if url_favorites else []

        # เพิ่มข้อมูลโปรไฟล์ลงใน list
        self.profiles_data.append(attr)
        self.profile_count += 1

        # ส่ง ProfileItem สำหรับการใช้ในการต่อไป
        self.logger.info(f"Scraped profile: {attr['username']}")  # เพิ่ม log สำหรับ profile ที่ถูก scrap
        yield ProfileItem(**attr)

        # บันทึกข้อมูลเมื่อถึง limit หรือทุกครั้งที่ scrap
        if self.profile_count % 100 == 0:  # บันทึกทุกๆ 100 โปรไฟล์
            self.save_to_json()

        # ตรวจสอบว่าเราถึง limit หรือยัง
        if self.profile_count >= self.end_limit:
            self.save_to_json()  # บันทึกข้อมูลเมื่อถึง limit

    def _extract_anime_uid(self, url):
        # ดึง UID ของอนิเมะจาก URL (คาดว่า URL จะมีรูปแบบ "/anime/{anime_id}")
        try:
            return url.split("/")[4]  # ดึง UID ของอนิเมะจาก URL
        except IndexError:
            self.logger.warning(f"Could not extract UID from URL: {url}")
            return None

    def _list2dict(self, attrs):
        # แปลงลิสต์เป็นดิกชันนารี
        attrs = dict(zip(attrs[::2], attrs[1::2]))
        return attrs

    def save_to_json(self):
        # เมื่อถึง limit หรือทุกๆ 100 โปรไฟล์ บันทึกข้อมูลทั้งหมดลงไฟล์ JSON
        self.logger.info(f"Saving {len(self.profiles_data)} profiles to JSON.")
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(self.profiles_data, f, ensure_ascii=False, indent=4)
