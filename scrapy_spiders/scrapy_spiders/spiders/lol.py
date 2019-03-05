# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy_spiders.items import LolItem


class LolSpider(scrapy.Spider):
    name = 'lol'
    allowed_domains = ['lol.qq.com']
    start_urls = ['http://lol.qq.com/biz/hero/champion.js']
    base_url = 'https://lol.qq.com/biz/hero/{}.js'
    base_img_url = 'http://ossweb-img.qq.com/images/lol/web201310/skin/big{}.jpg'

    def start_requests(self):
        headers = dict()
        headers['Referer'] = 'https://lol.qq.com/web201310/info-heros.shtm'
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            html_str = response.body.decode()
            heros_json_str = re.search(r'LOLherojs.champion={"keys":({.+?})', html_str).group(1)
            if heros_json_str is not None:
                heros_json = json.loads(heros_json_str)
                for hero_name in heros_json.values():
                    yield scrapy.Request(url=self.base_url.format(hero_name),
                                         callback=self.parse_skin,
                                         meta={'hero_name': hero_name}
                                         )

    def parse_skin(self, response):
        if response.status == 200:
            hero_name = response.meta['hero_name']
            html_str = response.body.decode()
            regex = re.compile(r'LOLherojs.champion.(%s)=(.+?});' % hero_name)
            hero_json_str = regex.search(html_str).group(2)
            if hero_json_str is not None:
                hero_data = json.loads(hero_json_str)['data']
                for skin in hero_data['skins']:
                    item = LolItem()
                    item['hero_name'] = '{}_{}'.format(hero_data['name'], hero_data['title'])
                    item['skin_name'] = skin['name']
                    item['img_url'] = self.base_img_url.format(skin['id'])
                    yield item
