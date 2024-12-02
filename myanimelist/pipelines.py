# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import numpy as np
from myanimelist.items import AnimeItem, ReviewItem, ProfileItem


class ProcessPipeline(object):
    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        item_class = item.__class__.__name__

        if item_class == "AnimeItem":
            item = self.process_anime(item)
        elif item_class == "ReviewItem":
            item = self.process_review(item)
        elif item_class == "ProfileItem":
            item = self.process_profile(item)

        return item

    def process_anime(self, item):
        # Handle 'score'
        if item.get('score') in [None, 'N/A']:
            item['score'] = np.nan
        else:
            try:
                item['score'] = float(item['score'].replace("\n", "").strip())
            except (ValueError, AttributeError):
                item['score'] = np.nan

        # Handle 'ranked'
        if item.get('ranked') in [None, 'N/A']:
            item['ranked'] = np.nan
        else:
            try:
                item['ranked'] = int(item['ranked'].replace("#", "").strip())
            except (ValueError, AttributeError):
                item['ranked'] = np.nan

        # Handle 'popularity'
        try:
            item['popularity'] = int(item['popularity'].replace("#", "").strip())
        except (ValueError, AttributeError):
            item['popularity'] = np.nan

        # Handle 'members'
        try:
            item['members'] = int(item['members'].replace(",", "").strip())
        except (ValueError, AttributeError):
            item['members'] = np.nan

        # Handle 'episodes'
        item['episodes'] = item.get('episodes', '').replace(",", "").strip()

        return item

    def process_review(self, item):
        # Handle 'score' for reviews
        try:
            item['score'] = float(item['score'].replace("\n", "").strip())
        except (ValueError, AttributeError):
            item['score'] = np.nan

        return item

    def process_profile(self, item):
        # Add custom processing logic for profiles if needed
        return item


class SaveLocalPipeline(object):
    def open_spider(self, spider):
        os.makedirs('data/', exist_ok=True)

        self.files = {}
        self.files['AnimeItem'] = open('data/animes.jl', 'w+')
        self.files['ReviewItem'] = open('data/reviews.jl', 'w+')
        self.files['ProfileItem'] = open('data/profiles.jl', 'w+')

    def close_spider(self, spider):
        for k, v in self.files.items():
            v.close()

    def process_item(self, item, spider):
        item_class = item.__class__.__name__

        # Save
        self.save(item_class, item)

        return item

    def save(self, item_class, item):
        line = json.dumps(dict(item)) + '\n'
        self.files[item_class].write(line)
