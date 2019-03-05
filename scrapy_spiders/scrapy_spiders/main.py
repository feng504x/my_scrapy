from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 传递参数 parms = 99
# execute('scrapy crawl tencent -a parms=99'.split())
# execute('scrapy crawl dangdang'.split())
execute('scrapy crawl lol'.split())
# execute('scrapy crawl github'.split())
# execute('scrapy crawl tieba'.split())
# execute('scrapy crawl circ -a parms=99 -a name=kenn'.split())

