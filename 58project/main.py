"""主程序--多进程爬虫的抓取"""
from multiprocessing import Pool #多进程导入
from channel_extract import channel_lists
from page_parsing import get_links_from

#用函数填入页码
def get_all_links_from(channel):
    for num in range(1,101):
        get_links_from(channel,num)


#创建进程池
#电脑上所有的程序都要从进程池中去取它分配的任务
#所以只要把函数塞进进程池，它就可以分配给4个CPU

if __name__ == '__main__':
    pool = Pool(processes=4) #括号内是指开多少个进程
    #map函数是把后面的一个个的传到前面运行
    """
    def dou(x):
        return x * 2
    print(list(map(dou,[1,2,3,4])))
    结果是[2,4,6,8]
    """
    pool.map(get_all_links_from,channel_lists.split())