# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class LolItem(scrapy.Item):
    # define the fields for your item here like:
    hero_name = scrapy.Field()
    skin_name = scrapy.Field()
    img_url = scrapy.Field()


class TencentSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_name = scrapy.Field()
    job_category = scrapy.Field()
    job_num = scrapy.Field()
    job_city = scrapy.Field()
    pub_date = scrapy.Field()


class SunSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    num = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    author = scrapy.Field()
    pub_date = scrapy.Field()
    content = scrapy.Field()
    have_img = scrapy.Field()
    img_url = scrapy.Field()


class DangDangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    f_cate = scrapy.Field()
    f_cate_id = scrapy.Field()
    s_cate = scrapy.Field()
    s_cate_id = scrapy.Field()
    s_cate_url = scrapy.Field()
    t_cate = scrapy.Field()
    t_cate_id = scrapy.Field()
    t_cate_url = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    desc = scrapy.Field()
    price = scrapy.Field()
    img_url = scrapy.Field()
    dtl_url = scrapy.Field()
    pub_date = scrapy.Field()
    score = scrapy.Field()
    w_num = scrapy.Field()
