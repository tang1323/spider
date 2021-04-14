
import re
import time
import json
from datetime import datetime
from selenium import webdriver
from scrapy import Selector
from urllib import parse



def parse_good():
    browser.get('https://shouji.jd.com/')
    # page_source就是运行js完后的html网页
    sel = Selector(text=browser.page_source)
    goods = sel.xpath('.//div[@id="lc-goods-rank__name"]/text()').extract()
    pass


if __name__ == "__main__":
    # chrome_options是无界面启动selenium

    browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
    # cookies = browser.get_cookies()
    # # 把cookies做一个转换
    # cookie_dict = {}
    # for item in cookies:
    #     cookie_dict[item['name']] = item["value"]

    # ua = UserAgent()
    # headers = {
    #     'User-Agent': ua.random
    # }
    # headers = {
    #     "User-Agent": ua.random
    # }

    parse_good()










