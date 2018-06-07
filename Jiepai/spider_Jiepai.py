"""
分析 Ajax 请求并抓取今日头条的街拍美图

流程框架
step1：抓取索引页内容
requests 请求目标站点，得到索引网页 HTML 代码，返回结果
step2：抓取详情页内容
解析返回结果，得到详情页的链接，并进一步抓取详情页的内容
step3：下载图片和保存数据库
将图片下载到本地，并把页面信息及图片 URL 保存至 MongoDB
step4：开启循环和多线程
对多页内容遍历，开启多线程提高抓取速度

"""

import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
import re
from config import *
import pymongo
import os
from hashlib import md5  #导入MD5判断
from multiprocessing import Pool

client = pymongo.MongoClient(mongo_url,connect=False)
db = client[mongo_db]

headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
}

def get_page_index(offset,keyword): #获取索引页的json
     #参数通过分析页面的ajax请求获得
    data = {
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':'20',
        'cur_tab':'1',
        'from':'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data) #将字典对象转化为请求对象
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引出错')
        return None

def parse_page_index(html): #获取索引页过来的json的图片url地址
    data = json.loads(html) #json字符串转化为json对象
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

def get_page_detail(url): # 获取详情
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错',url)
        return None
def parse_page_detail(html,url): #解析详情页
    soup = BeautifulSoup(html,'lxml')
    title = soup.title.string
    print(title)
    images_pattern = re.compile(r'gallery:.*?parse\("(.*?)"\),',re.S) #加 r 表示不转义
    result = re.search(images_pattern,html)
    result = re.sub(r'\\','',result.group(1))
    if result:
        data = json.loads(result)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:download_image(image)
            return {
                'title':title,
                'url':url,
                'images':images
            }

#存储在 mongodb 上
def save_to_mongodb(result):
    if db[mongo_table].insert(result):
        print('存储到 mongodb 成功',result)
        return True
    return False

#通过地址下载图片的二进制流
def download_image(url):
    print('正在下载',url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content) # content 返回为二进制文件，一般图片用contenf， text 保存为文本
        return None
    except RequestException:
        print('请求图片出错', url)
        return None

#将二进制信息保存到本地  也就是图片
def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_page_index(offset,keyword)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html,url)
            if result:
                save_to_mongodb(result)

if __name__ == '__main__':
    groups = [x * 20 for x in range(group_start,group_end + 1)]
    pool = Pool()
    pool.map(main,groups)