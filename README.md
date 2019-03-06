# my_scrapy
英雄联盟皮肤scrapy爬虫


#### 简介
- scrapy基于twisted异步网络框架的爬虫框架, 爬虫效率高, 高度定制化
- spiders目录下的lol.py 就是捉取ylol英雄皮肤的爬虫
- 正常来说, 运行main.py就可以开启爬虫

#### 注意
- 运行爬虫之前, 要先安装好Python以及第三方库的爬虫环境, 第三方库的要求在requirements.txt

#### 本代码可以加强的地方
- 数据库存入时候的去重, 加入唯一索引
- 请求的时候对cookie，headers的处理，refer的处理，代理ip的处理, 防止被封
- 如果想更快的话,可以配合scrapy_redis做分布式爬虫
