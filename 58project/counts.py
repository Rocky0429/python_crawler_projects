"""
创建用来计数的监控程序
用来看已经抓了多少数据
"""
import time
from page_parsing import url_list

while True:
    print(url_list.find().count())
    time.sleep(5)