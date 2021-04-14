from selenium import webdriver
from scrapy import Selector
import json

import requests
from jd_spider.models import *

"""
这是虽然是启动了selenium，但还是用静态网页的爬取方法
这里是分析了网络请求后的js文件下内容
因为都很多内容都是放在js渲染之后的，所以要做进一步分析url的形态
这样也能用requests请求回来
至于怎么用selenium来获取动态网页己经渲染回来的网页，在js_selenium_dynamic中
"""
def parse_good(good_id):
    good_url = 'https://item.jd.com/{}.html'.format(good_id)
    html = requests.get(good_url, headers=headers, cookies=cookie_dict).text
    sel = Selector(text=html)

    # 提取商品的基本信息
    good = Good(id=good_id)
    # 这个name是有回车换行符的，这里我们用"".join().strip
    name = "".join(sel.xpath(".//div[@class='sku-name']/text()").extract()[0]).strip()

    # 这个是在js里的字段,获取商品的价格
    price_url = "https://p.3.cn/prices/mgets?type=1&pdtk=&skuIds=J_{}&source=item-pc".format(good_id)
    # 用strip()处理回车换行符
    price_text = requests.get(price_url, headers=headers, cookies=cookie_dict).text.strip()
    # loads加来的是list类型,dumps是一个对象(字符串类型)
    price_list = json.loads(price_text)
    print(type(price_list))

    if price_list:
        # 价格
        price = float(price_list[0]["p"])

    # 获取商品的评价
    evaluate_url = 'https://club.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'.format(good_id, 0)
    evaluate_json = json.loads(requests.get(evaluate_url, headers=headers, cookies=cookie_dict).text)
    max_page = 0
    # 获取多少页
    max_page = evaluate_json["maxPage"]

    # 一些标签都在这里
    statistics = evaluate_json["hotCommentTagStatistics"]

    # 评论都 在这里
    evaluate = evaluate_json["comments"]
    # 有很多，就做一个循环，都是这样取
    for res in range(0, 10):
        content = evaluate[res]["content"]
    pass



if __name__ == "__main__":
    browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
    browser.get('https://item.jd.com/100016034400.html')
    import time

    time.sleep(9)

    # 获取一下cookies
    cookies = browser.get_cookies()
    # 把cookies做一个转换
    cookie_dict = {}
    for item in cookies:
        cookie_dict[item['name']] = item["value"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111"
    }
    # print(requests.get("https://club.jd.com/comment/productPageComments.action?productId=100016034400&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1",headers=headers, cookies=cookie_dict).text)
    parse_good(100016034400)


















