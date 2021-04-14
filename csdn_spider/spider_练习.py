import re
import ast
from urllib import parse    # 拼接url的
from datetime import datetime


import requests
from scrapy import Selector


from csdn_spider.models import *


domain = 'https://bbs.csdn.net/'


# 把放在js里面的代码获取下来，因为数据就放在里面
def get_notes_json():
    # 这里是获取json的一个文本，还要进一步提取
    left_menu_text = requests.get("https://bbs.csdn.net/dynamic_js/left_menu.js?csdn").text

    # search是可以从任意地方开始，哪怕回车换行符都会去匹配
    # 如果是match的话就从第一行开始
    """
    (.*?])这个是取到第一个]就结束了
    (.*])是匹配最后一个]才结束
    """
    nodes_str_match = re.search("forumNodes: (.*])", left_menu_text)
    if nodes_str_match:
        # 在要爬取的js里有"null"，python里的json会抛异常的，这里所以要更换成一个None
        nodes_str = nodes_str_match.group(1).replace("null", "None")
        # ast.literal_eval转换成list
        nodes_list = ast.literal_eval(nodes_str)
        # print(nodes_list)
        return nodes_list
    # 如果遇到反爬，那就返回一个空列表
    return []



# 将js的格式提取出url到list中
url_list = []


def process_nodes_list(nodes_list):
    for item in nodes_list:
        if "url" in item:
            # item的url不为空才放进来
            if item["url"]:
                print(item["url"])
                url_list.append(item["url"])

            # 有的还有children文件
            if "children" in item:
                print(item["children"])
                # 这再提取这个children
                process_nodes_list(item["children"])


# 我们获取第一个层url就行了
def get_level1_list(nodes_list):
    # 这是第一层的url
    level1_url = []
    for item in nodes_list:
        # item的url不为空才放进来
        if "url" in item and item["url"]:
            print(item["url"])
            # item的url不为空才放进来
            level1_url.append(item["url"])

    return level1_url



# 获取最终需要爬取的url
def get_last_urls():
    """
    从这里启动，第1步
    :return:
    """
    nodes_list = get_notes_json()   # 第二步，这个函数有返回值，要拿一个值nodes_list接收一下
    process_nodes_list(nodes_list)  # 第三步，这是进一步提取url出来
    # level1_url是第一层url
    level1_url = get_level1_list(nodes_list)    # 第4步
    """
    因为process_nodes_list是得到所有的url
    而level1_url是得到左边第一层的url
    所 以下面的last_url = []做一个去除
    重点！！！！
    last_url就是得到的最后要爬取的所有的url
    """
    last_url = []
    for url in url_list:
        # 把不是第一层的url放在last_url里面
        # url_list和level1_url可能有重复的url，这里做一个去除，得到最终的url放在last_url
        if url not in level1_url:
            last_url.append(url)

    # 这是爬取精华与完结的url，这是拼url
    all_urls = []
    for url in last_url:
        # 用parse.urljoin拼接域名
        all_urls.append(parse.urljoin(domain, url))
        print(all_urls)
        all_urls.append(parse.urljoin(domain, url+"/recommend"))
        print(all_urls)
        all_urls.append(parse.urljoin(domain, url + "/closed"))
        print(all_urls)
    return all_urls


# 开始程序
get_last_urls()
# last_urls = get_last_urls()
# for url in last_urls:
#     get_last_urls()




















