# -*- coding: utf-8 -*-
import scrapy
import logging
from scrapy_spiders.items import TencentSpiderItem
logger = logging.getLogger('TencentSpider')


class TencentSpider(scrapy.Spider):
    name = 'tencent'
    allowed_domains = ['tencent.com']
    start_urls = ['https://hr.tencent.com/position.php']

    def __init__(self, parms=None, *args, **kwargs):
        super(TencentSpider, self).__init__(*args, **kwargs)
        # 接收参数
        print(parms)
        self.part_url = 'https://hr.tencent.com/'

    def start_requests(self):
        for url in self.start_urls:
            req = scrapy.Request(url=url, callback=self.parse)
            yield req

    def parse(self, response):
        if response.status == 200:
            info_list = response.xpath("//table[@class='tablelist']//tr")[1:-1]
            for info in info_list:
                item = TencentSpiderItem()
                item['job_name'] = info.xpath("./td[1]/a/text()").extract_first()
                item['job_category'] = info.xpath("./td[2]/text()").extract_first()
                item['job_num'] = info.xpath("./td[3]/text()").extract_first()
                item['job_city'] = info.xpath("./td[4]/text()").extract_first()
                item['pub_date'] = info.xpath("./td[5]/text()").extract_first()
                yield item

            # 判断下一页
            next_page_url = response.xpath("//a[text()='下一页']/@href").extract_first()
            # print(next_page_url)
            if next_page_url != 'javascript:;':
                yield scrapy.Request(url=self.part_url+next_page_url,
                                     callback=self.parse
                                     )

