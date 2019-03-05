# -*- coding: utf-8 -*-
import scrapy
from scrapy_spiders.items import SunSpiderItem


class SunSpider(scrapy.Spider):
    name = 'sun'
    allowed_domains = ['sun0769.com']
    start_urls = ['http://wz.sun0769.com/index.php/question/questionType?type=4&page=0']

    def parse(self, response):
        if response.status == 200:
            tr_list = response.xpath("//table[@width='940']//table//tr")
            for tr in tr_list:
                item = SunSpiderItem()
                item['num'] = tr.xpath("./td[1]/text()").extract_first()
                item['title'] = '_'.join(tr.xpath("./td[2]/a[2]//text()").extract())
                item['status'] = tr.xpath("./td[3]/span/text()").extract_first()
                item['author'] = tr.xpath("./td[4]/text()").extract_first()
                item['pub_date'] = tr.xpath("./td[5]/text()").extract_first()
                item['pub_date'] = tr.xpath("./td[5]/text()").extract_first()

                # 判断有没有图片
                item['have_img'] = 1 if '[图]' in item['title'] else 0

                detail_url = tr.xpath("./td[2]/a[2]/@href").extract_first()
                yield scrapy.Request(url=detail_url,
                                     meta={'item': item},
                                     callback=self.parse_dtl
                                     )
            # 判断下一页
            next_page_url = response.xpath("//a[text()='>']/@href").extract_first()

            # print(next_page_url)
            if next_page_url:
                yield scrapy.Request(url=next_page_url,
                                     callback=self.parse
                                     )

    def parse_dtl(self, response):
        """解释详情页"""
        if response.status == 200:
            item = response.meta['item']
            # 详情页的html有两种情况,需要判断
            div = response.xpath("//div[@class='wzy1']").extract_first()

            if item['have_img']:
                if div:
                    content = response.xpath("//div[@class='wzy1']/table[2]//td[1]//div[@class='contentext']//text()").extract()
                    item['content'] = content
                    item['img_url'] = ['http://wz.sun0769.com' + i for i in response.xpath("//div[@class='wzy1']/table[2]//td[1]//img/@src").extract()]
                else:
                    content = response.xpath("//div[contains(@class,'p3')]//div[@class='contentext']//text()").extract()
                    item['content'] = content
                    item['img_url'] = ['http://wz.sun0769.com' + i for i in response.xpath("//div[contains(@class,'p3')]//img/@src").extract()]
            else:
                if div:
                    content = response.xpath("//div[@class='wzy1']/table[2]//td[1]/text()").extract()
                    item['content'] = content
                else:
                    content = response.xpath("//div[contains(@class,'p3')]//div[contains(@class,'c1')]/text()").extract()
                    item['content'] = content

                item['img_url'] = None

            yield item


