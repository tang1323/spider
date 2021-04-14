import requests

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

print(requests.get("https://bbs.csdn.net/forums/ios", cookies=cookie_dict).text)

















