# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import txmongo
import logging
import scrapy
# import MySQLdb
from scrapy import signals
from scrapy.exceptions import DropItem
from traceback import print_exc
from pymongo.errors import AutoReconnect, DuplicateKeyError
from twisted.internet import defer
# mysql数据库的异步库
from twisted.enterprise import adbapi
from scrapy_spiders.utils import trip_text
# from scrapy_spiders.tools import db, DBCONFIG
from scrapy.pipelines.images import ImagesPipeline
from scrapy_redis.connection import get_redis_from_settings

logger = logging.getLogger(__name__)


class MyImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['skin_name'] == 'default':
            item['skin_name'] = '默认皮肤'
        meta = {'hero_name': item['hero_name'], 'skin_name': item['skin_name']}
        # 循环每一张图片地址下载，若传过来的不是集合则无需循环直接yield
        yield scrapy.Request(url=item['img_url'], meta=meta)

        # 重命名，若不重写这函数，图片名为哈希，就是一串乱七八糟的名字

    def file_path(self, request, response=None, info=None):

        # 接收上面meta传递过来的图片名称
        hero_name = request.meta['hero_name']
        skin_name = request.meta['skin_name']
        # 过滤windows字符串，不经过这么一个步骤，你会发现有乱码或无法下载
        skin_name = re.sub(r'[？\\*|“<>:/]', '', skin_name)
        # 分文件夹存储的关键：{0}对应着name；{1}对应着image_guid
        filename = u'{0}/{1}.jpg'.format(hero_name, skin_name)
        return filename

    def item_completed(self, results, item, info):
        """下载图片后"""
        if isinstance(item, dict) or self.images_result_field in item.fields:
            item[self.images_result_field] = [x for ok, x in results if ok]
        # 下载成功设置status=1
        item['status'] = 1
        # 处理失败的情况, 图片下载失败默认会有retry中间件重试,重试次数后还是失败
        if not results[0]:
            # 将失败的信息存入redis
            logger.error("download {} failed!!!!!!".format(item['img_url']))
            item['status'] = 0

            # raise DropItem("drop item {} !!!!!!".format(item['img_url']))

        return item

class BaiduSpiderPipeline(object):
    def process_item(self, item, spider):
        logger.info('this is pipeline!!!!!!!!!')
        return item


class MongodbPipeline(object):

    # mongodb数据库名称
    # def __init__(self, mongo_uri, mongo_db, mongo_collection):
    #     self.mongo_uri = mongo_uri
    #     self.mongo_db = mongo_db
    #     self.mongo_collection = mongo_collection


    # @classmethod
    # def from_crawler(cls, crawler):
    #     # 从settings 获取 MONGO_URI，MONGO_DATABASE, 传入__init__方法
    #     obj = cls(
    #         mongo_uri=crawler.settings.get('MONGO_URI'),
    #         mongo_db=crawler.settings.get('MONGO_DATABASE'),
    #         mongo_collection=crawler.settings.get('MONGO_COLLECTION'),
    #     )
    #     return obj

    def open_spider(self, spider):
        mongo_db = spider.settings.get('MONGO_DATABASE')
        mongo_collection = spider.settings.get('MONGO_COLLECTION')
        # 初始化连接池
        self.client_pool = txmongo.MongoConnection(pool_size=5)
        self.collection = self.client_pool[mongo_db][mongo_collection]

    def close_spider(self, spider):
        # 数据库关闭
        self.client_pool.disconnect()

    @staticmethod
    def process_content(content_list):
        """
        处理内容中的空白字符
        :param content_list:  list()
        :return:
        """
        content_list = [trip_text(content) for content in content_list]
        return [content for content in content_list if len(content) > 0]

    def process_item(self, item, spider):
        # 处理数据
        # if item['desc'] is not None:
        #     item['desc'] = self.process_content(item['desc'])
        # if item['author'] is not None:
        #     item['author'] = trip_text(item['author'])
        # if item['title'] is not None:
        #     item['title'] = trip_text(item['title'])
        # tieba
        # if item['lou_list'] is not None:
        #     for lou_info in item['lou_list']:
        #         lou_info['author'] = trip_text(lou_info['author'])
        #         lou_info['content'] = self.process_content(lou_info['content'])

        # lol爬虫下载失败的时候才保存入库
        # 异步插入数据
        if item['status'] == 0:
            self.mongo_insert(dict(item))
        # 切记 一定要返回item进行后续的pipelines 数据处理
        return item

    @defer.inlineCallbacks
    def mongo_insert(self, doc):
        try:
            # insert方法返回_id
            result = yield self.collection.insert(doc, safe=True)
        except AutoReconnect as e:
            # txmongo 有重连功能, 这里要捕捉一下重连的错误
            # print(e)
            pass
        except DuplicateKeyError:
            # 重复的数据跳过
            print('DuplicateKey pass')
            pass
        else:
            return result

    @defer.inlineCallbacks
    def mongo_find(self, spec, limit=10):
        result = yield self.collection.find(spec, limit=limit)
        return result


# class MysqlPipeline(object):
#     """
#     Mysql异步库Pipeline
#     """
#     # Twisted只是提供一个异步容器，本身没提供数据库链接
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):
#         # 参数settings从项目的settings.py中获取
#         # 从配置中获取信息
#         dbparms = dict(
#             host=DBCONFIG['host'],
#             db=DBCONFIG['db'],
#             user=DBCONFIG['user'],
#             passwd=DBCONFIG['passwd'],
#             port=DBCONFIG['port'],
#             charset='utf8',
#             cursorclass=MySQLdb.cursors.DictCursor,
#             use_unicode=True
#         )
#         dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         # 使用twisted将mysql插入编程异步执行
#         # 第一个参数是我们定义的函数
#         query = self.dbpool.runInteraction(self.do_insert, item)
#         # 错误处理
#         query.addErrback(self.handle_error)
#         return item
#
#     # 错误处理函数
#     def handle_error(self, falure):
#         print(falure)
#
#     def do_insert(self, cursor, item):
#         # print threading.current_thread()
#         # 执行具体的插入语句,不需要commit操作,Twisted会自动进行
#         insert_sql = """
#                     insert ignore into qqzone(ablum_id)
#                     VALUES (%(ablum_id)s)
#                     """
#         cursor.execute(insert_sql, dict(item))
#         print(insert_sql % dict(item))
#
#     def close_spider(self, spider):
#         # 数据库关闭
#         self.dbpool.close()