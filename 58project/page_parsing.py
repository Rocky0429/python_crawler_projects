from bs4 import BeautifulSoup
import requests
import time
import pymongo

#设置数据库
client = pymongo.MongoClient('localhost',27017)
ceshi = client['ceshi']
url_list = ceshi['url_list3']
item_info = ceshi['item_info']

#用 spider1 爬取商品链接
def get_links_from(channel,pages,who_sells = 0):
    #http://bj.58.com/shuma/0/pn3/
    list_view = '{}{}/pn{}/'.format(channel,str(who_sells),str(pages))
    wb_data = requests.get(list_view)
    time.sleep(1)
    soup = BeautifulSoup(wb_data.text,'lxml')
    if soup.find('td','t'): #样式为 t 的 td 的标签  < td class = t >
        for link in soup.select('td.t > a.t'):
            item_link = link.get('href').split('?')[0]
            url_list.insert_one({'url':item_link})
            print(item_link)
    else:
        pass
        #Nothing!
#get_links_from('http://bj.58.com/shuma/',3)

#用 spider2 爬取商品详细信息
def get_item_info(url):
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text,'lxml')
    #因为有的页面会被删除，删除的页面出现404，这样的页面不能爬取
    no_longer_exist = '404' in soup.find('script',type = "text/javascript").get('src').split('/')
    if no_longer_exist:
        pass
    else:
        title = soup.title.text
        price = soup.select('span.price.c_f50')[0].text
        data = soup.select('.time')[0].text
        area = list(soup.select('span.c_25d a')[0].stripped_strings) if soup.find_all('span','c_25d') else None
        item_info.insert_one({'title':title, 'price':price,'data':data,'area':area})
        print({'title':title, 'price':price,'data':data,'area':area})







