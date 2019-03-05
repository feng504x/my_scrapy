import copy
import requests
import re
import scrapy
import json
from retrying import retry
# 分布式爬虫的实现
from scrapy_redis.spiders import RedisSpider
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from scrapy_spiders.items import DangDangItem
from scrapy_spiders.tools.utils import random_headers


class DangdangSpider(RedisSpider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    # 分布式爬虫使用的redis_key
    redis_key = 'dangdang:start_urls'
    # start_urls = ['http://e.dangdang.com/list-WY1-dd_sale-0-1.html']
    custom_settings = {
        'REDIRECT_ENABLED': False,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 408, 302]
    }
    # def start_requests(self):
    #     scripts = """
    #                  function main(splash, args)
    #                       splash.images_enabled = false
    #                       splash:go(args.url)
    #                       local scroll_to = splash:jsfunc("window.scrollTo")
    #                       scroll_to(0, 3000)
    #                       splash:wait(1)
    #                       return {html=splash:html()}
    #                  end
    #               """
    #
    #     for url in self.start_urls:
    #         yield SplashRequest(url, self.parse, endpoint='execute',
    #                             args={'lua_source': scripts, 'url': url})
    def parse(self, response):
        if response.status == 200:
            # 先获取第一级的分类所在的元素, 最后三个分类不取...
            first_lv_list = response.xpath("//div[contains(@class,'first_level') and contains(@class,'publisher')]")[:-3]

            for div_el in first_lv_list:
                item = DangDangItem()
                item['f_cate'] = div_el.xpath(".//h3/@dd_name").extract_first()
                item['f_cate_id'] = div_el.xpath(".//h3/@data-type").extract_first()

                # 第二级分组
                second_lv_list = div_el.xpath("./ul[@class='second_level']/li")
                for li_el in second_lv_list:
                    item['s_cate'] = li_el.xpath(".//h4/@dd_name").extract_first()
                    item['s_cate_id'] = li_el.xpath(".//h4/@data-type").extract_first()
                    item['s_cate_url'] = li_el.xpath("./a/@href").extract_first()

                    # 第三级分组
                    third_lv_list = li_el.xpath("./ul[@class='third_level']/a")
                    # 判断第三级分组是否存在
                    if third_lv_list:
                        for a_el in third_lv_list:
                            item['t_cate'] = a_el.xpath("./li/@dd_name").extract_first()
                            item['t_cate_id'] = a_el.xpath("./li/@data-type").extract_first()
                            item['t_cate_url'] = a_el.xpath("./@href").extract_first()
                            if item['t_cate_url']:
                                req = scrapy.Request(url=item['t_cate_url'],
                                                     callback=self.parse_book_list,
                                                     meta={'item': copy.deepcopy(item)}
                                                     )
                                yield req
                    else:
                        # 不存在三级分组的情况
                        if item['s_cate_url']:
                            item['t_cate'] = item['t_cate_id'] = item['t_cate_url'] = None
                            req = scrapy.Request(url=item['s_cate_url'],
                                                 callback=self.parse_book_list,
                                                 meta={'item': copy.deepcopy(item)}
                                                 )
                            yield req

    @inlineCallbacks
    def parse_book_list(self, response):
        """解释书本列表页"""
        item = response.meta['item']
        if response.status == 200:
            # 按元素分组
            book_list = response.xpath("//div[contains(@class,'book_list')]/a[@dd_name]")
            # if book_list:
            #     # 统计第一页书的数量
            #     book_count = len(book_list)
            #
            #     for book_el in book_list:
            #         item['title'] = book_el.xpath("./@title").extract_first()
            #         item['dtl_url'] = book_el.xpath("./@href").extract_first()
            #         item['author'] = book_el.xpath("./@dd_name").extract_first()
            #         item['price'] = book_el.xpath(".//div[@class='price']/span/text()").extract_first()
            #         item['desc'] = book_el.xpath(".//div[@class='des']//text()").extract()
            #         item['img_url'] = book_el.xpath(".//img/@src").extract()
            #         dtl_req = scrapy.Request(url=item['dtl_url'],
            #                                  callback=self.parse_book_dtl,
            #                                  meta={'item': copy.deepcopy(item)}
            #                                  )
            #         yield dtl_req
            # 统计第一页书的数量
            book_count = len(book_list)
            # # 大于等于21, 判断有下一页,
            # js动态分页, 可能要用splash实现下滑加载
            if book_count >= 21:
                cate_id = item['t_cate_id'] if item['t_cate_id'] else item['s_cate_id']
                get_total_url = 'http://e.dangdang.com/media/api.go?action=mediaCategoryLeaf&promotionType=1&deviceSerialNo=html5&macAddr=html5&channelType=html5&permanentId=20181225180833416314687785189703839&returnType=json&channelId=70000&clientVersionNo=5.8.4&platformSource=DDDS-P&fromPlatform=106&deviceType=pconline&token=&start=0&end=0&category={}&dimension=dd_sale&order=0'.format(cate_id)
                # 请求一次获取分类书本总数
                # 这里用了deferToThread异步线程方法, 阻塞的代码放到twisted的其他线程去做, 当有结果的时候,返回结果
                total = yield deferToThread(self.get_cate_total, get_total_url)

                if total is None:
                    self.logger.error("{} get cate total fail!!!!!!!!!!!!!!".format(cate_id))
                    # 获取total 则退出
                    return
                # 操作成功则输出
                print("cate_id : {} total : {}".format(cate_id, total))

                # 默认分类页面有0-20共21本书的信息, 所以从21开始算起
                i = 0
                # 每次获取多少本的书
                interval = 99
                req_list = list()
                next_part_url = 'http://e.dangdang.com/media/api.go?action=mediaCategoryLeaf&promotionType=1&deviceSerialNo=html5&macAddr=html5&channelType=html5&permanentId=20181225180833416314687785189703839&returnType=json&channelId=70000&clientVersionNo=5.8.4&platformSource=DDDS-P&fromPlatform=106&deviceType=pconline&token=&start={}&end={}&category={}&dimension=dd_sale&order=0'
                while i <= total:
                    next_url = next_part_url.format(i, i + interval, cate_id)
                    next_req = scrapy.Request(url=next_url,
                                              callback=self.parse_book_json,
                                              meta={'item': item}
                                              )
                    req_list.append(next_req)
                    i = i + interval + 1
                # print(req_list)
                # 这里需要返回一个可迭代的对象, 因为engine会调用next()
                return req_list

    def parse_book_json(self, response):
        """解释josn格式的书本信息"""
        if response.status == 200:
            book_infos = json.loads(response.body)
            if book_infos['status']['code'] != 0:
                self.logger.error('get book json fail!!!!!!!!!!!')
                return

            for book in book_infos['data']['saleList']:
                item = response.meta['item']
                item['title'] = book['mediaList'][0]['title']
                item['dtl_url'] = 'http://e.dangdang.com/products/{}.html'.format(
                    book['mediaList'][0]['saleId'])
                item['author'] = book['mediaList'][0]['authorPenname'] if 'authorPenname' in book['mediaList'][0] else None
                item['price'] = book['mediaList'][0]['salePrice'] if 'salePrice' in book['mediaList'][0] else None
                item['desc'] = book['mediaList'][0]['descs']
                item['img_url'] = book['mediaList'][0]['coverPic']
                yield scrapy.Request(url=item['dtl_url'],
                                     callback=self.parse_book_dtl,
                                     meta={'item': item}
                                     )

    # 使用了重试库retrying
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def _get_cate_total(self, url):
        print('*' * 20)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'User-Agent': random_headers()
        }
        res = requests.get(url=url, headers=headers, timeout=3)
        assert res.status_code == 200
        total = res.json()['data']['total']
        return total

    def get_cate_total(self, url):
        """
        请求url获得分类书本的总数
        :param url:
        :return:
        """
        try:
            total = self._get_cate_total(url)
        except Exception as e:
            self.logger.error(e)
            return None
        else:
            return total

    def parse_book_dtl(self, response):
            """解释书本详情页"""
            item = response.meta['item']
            if response.status == 200:
                item['score'] = response.xpath("//em[@class='readIndex']/text()").extract_first()
                item['w_num'] = response.xpath("//div[@class='explain_box']/p[4]/text()").extract_first()
                item['pub_date'] = response.xpath("//div[@class='explain_box']/p[3]/text()").extract_first()
                if item['w_num'] and re.search(r"\d+?", item['w_num']):
                    item['w_num'] = item['w_num'].split('：')[-1]
                else:
                    item['w_num'] = None
                if item['pub_date'] and re.search(r"\d+?", item['pub_date']):
                    item['pub_date'] = item['pub_date'].split('：')[-1]
                else:
                    item['pub_date'] = None
                yield item

