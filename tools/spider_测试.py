
import requests
from scrapy import Selector


# def parse_list(url):
url = "https://bbs.csdn.net/topics/397712664?page=2"

res_text = requests.get(url).text
# 做成一个选择器，这样可以用selector选择器提取数据
sel = Selector(text=res_text)
print(sel)


if __name__ == "__main__":
    from selenium import webdriver

    browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
    browser.get('https://bbs.csdn.net/')
    import time
    time.sleep(5)

    # 获取一下cookies
    cookies = browser.get_cookies()
    # 把cookies做一个转换
    cookie_dict = {}
    for item in cookies:
        cookie_dict[item['name']] = item["value"]



    # parse_list("https://bbs.csdn.net/topics/397712664?page=2")
#









