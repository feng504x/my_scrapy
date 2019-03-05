# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class CircSpider(CrawlSpider):
    name = 'circ'
    allowed_domains = ['circ.gov.cn']
    start_urls = ['http://circ.gov.cn/web/site0/tab5240/module14430/page1.htm']
    custom_settings = {
                        'DOWNLOAD_DELAY': 0
                        }

    rules = (
        Rule(LinkExtractor(allow=r'/web/site0/tab5240/info\d+\.htm'), callback='parse_item'),
        Rule(LinkExtractor(allow=r'/web/site0/tab5240/module14430/page(\d+).htm'), follow=True),
    )

    def parse_item(self, response):
        self.logger.info(self.parms)
        self.logger.info(self.name)
        item = {}
        item['title'] = re.findall(r'<!--TitleStart-->(.*?)<!--TitleEnd-->', response.body.decode())[0]
        item['date'] = re.findall(r'发布时间：(20\d{2}-\d{2}-\d{2})', response.body.decode())[0]
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # return item
        yield item
