# 英雄联盟皮肤scrapy爬虫



#### 简介
- scrapy基于twisted异步网络框架的爬虫框架, 爬虫效率高, 高度定制化
- spiders目录下的lol.py 就是捉取ylol英雄皮肤的爬虫
- 正常来说, 运行main.py就可以开启爬虫
- img文件夹是最近下载好的英雄联盟皮肤图片,福利福利

#### 注意
- 运行爬虫之前, 要先安装好Python以及第三方库的爬虫环境, 第三方库的要求在requirements.txt
- 如需自定义下载文件路径,scrapy下载配置项等, 在settings.py文件下

#### 本代码可以加强的地方
- 数据库存入时候的去重, 加入唯一索引
- 请求的时候对cookie，headers的处理，refer的处理，代理ip的处理, 防止被封
- 如果想更快的话,可以配合scrapy_redis做分布式爬虫

#### 最近的优化
- 图片下载过后,不会重新下载, 除非超过设置的日期, 默认设置是90天
- 虽然scrapy有重试中间件, 但由于各种各样的原因, 图片下载还是会有机会下载失败, 
  所以最后会将下载失败的图片信息,存入mongodb中, 以便之后的处理

#### 总结
- 如果你们遇到什么问题, 可以提问
- 如果你们觉得好用的话, 可以给我几个star, hah 

#### 爬虫截图

![](https://i.imgur.com/2BVaN2H.jpg)
# spider文件
![](https://i.imgur.com/rHgNOji.jpg)
# pipeline文件
![](https://i.imgur.com/kWwxKwI.jpg)

![](https://i.imgur.com/bCNeTgZ.jpg)

![](https://i.imgur.com/7Kz2rnZ.jpg)

![](https://i.imgur.com/j282aWs.jpg)
