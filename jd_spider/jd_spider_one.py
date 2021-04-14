import requests
# 1.商品的价格


# print(requests.get("https://p.3.cn/prices/mgets?type=1&pdtk=&skuIds=J_100016034400&source=item-pc").text)
from selenium import webdriver

browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
browser.get('https://www.jd.com/')
import time
time.sleep(5)

# 获取一下cookies
cookies = browser.get_cookies()
# 把cookies做一个转换
cookie_dict = {}
for item in cookies:
    cookie_dict[item['name']] = item["value"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111"
}
print(requests.get("https://club.jd.com/comment/productPageComments.action?productId=100016034400&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1", headers=headers, cookies=cookie_dict).text)









