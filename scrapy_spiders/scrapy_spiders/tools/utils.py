import random
import re
from scrapy_spiders.tools.user_agents import agents


# 生成随机头
def random_headers():
    agent = random.choice(agents)
    return agent


# 将获取到的数据进行清洗规整
def trip_text(t):
    # t = "".join(t.split())
    return re.sub(r'\xa0|\s', '', t)

