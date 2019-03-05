# -*- coding: utf-8 -*-
import scrapy
import re


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/login']
    custom_settings = {
        'HTTPCACHE_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_spiders.middlewares.RandomUserAgentMiddleware': None,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            print(self.start_urls.index(url))
            """第一次请求一下登录页面，设置开启cookie使其得到cookie，设置回调函数"""
            yield scrapy.Request(url, meta={'cookiejar': self.start_urls.index(url)}, callback=self.parse)

    def parse(self, response):
        # 响应Cookies
        # 查看一下响应Cookie，也就是第一次访问注册页面时后台写入浏览器的Cookie
        Cookie1 = response.headers.getlist('Set-Cookie')
        print('后台首次写入的响应Cookies：', Cookie1)

        cookiejar = response.meta['cookiejar']
        utf8 = response.xpath("//input[@name='utf8']/@value").extract_first()
        auth_token = response.xpath("//input[@name='authenticity_token']/@value").extract_first()
        commit = response.xpath("//input[@name='commit']/@value").extract_first()
        # post_data = {
        #              'login': 'feng504x',
        #              'password': '86034603a',
        #              'utf8': utf8,
        #              'authenticity_token': auth_token,
        #              'commit': commit
        #             }
        post_data = {
            'login': 'feng504x',
            'password': '86034603a',
        }
        headers = {
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'Cache-Control': 'max-age=0',
            # 'Connection': 'keep-alive',
            # 'Content-Type': 'application/x-www-form-urlencoded',
            # 'Host': 'github.com',
            # 'Origin': 'https://github.com',
            'Referer': 'https://github.com/login',
            # 'Upgrade-Insecure-Requests': 1,
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
        }
        # post提交
        yield scrapy.FormRequest.from_response(
            response,
            formdata=post_data,
            callback=self.after_login,
            meta={'cookiejar': response.meta['cookiejar']},
        )

    def after_login(self, response):
        # 请求Cookie
        Cookie2 = response.request.headers.getlist('Cookie')
        print('登录时携带请求的Cookies：', Cookie2)

        yield scrapy.Request(url='https://github.com/feng504x', callback=self.parse_person)

    def parse_person(self, response):
        print('person info~~~~~')