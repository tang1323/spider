

import time
import random
import requests
from io import BytesIO
from PIL import Image   # 这是安装pillow包，专门处理图像的
from selenium.webdriver import ActionChains     # 导入鼠标动作链对象
from scrapy import Selector
import urllib.request
from selenium import webdriver
import base64
"""这是用快识别打码平台的登录方式"""

# bilibili的帐号和密码
USERNAME = '13232732408'
PASSWORD = '130796abc'

# 快识别打码的平台
KUAI_USERNAME = 'tang1323'
KUAI_PASSWORD = '130796abc'
# KUAI_SOFT_ID = 907581
# KUAI_KIND = 9004


class BiliBiliLogin():
    # 初始化
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
        self.browser.maximize_window()  # 最大化浏览器
        self.username = USERNAME
        self.password = PASSWORD

    def input_open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        user = self.browser.find_element_by_css_selector("#login-username")
        password = self.browser.find_element_by_css_selector("#login-passwd")
        user.send_keys(self.username)
        password.send_keys(self.password)
        login_btn = self.browser.find_element_by_css_selector(".btn.btn-login")
        # 随机暂停几秒
        time.sleep(random.random() * 3)
        # 点击登陆按钮
        login_btn.click()
        time.sleep(2)

    def pick_code(self):
        """保存图片到本地项目"""
        # page_source就是运行js完后的html网页
        sel_css = Selector(text=self.browser.page_source)

        img_urls = sel_css.css(".geetest_item_wrap img::attr(src)").extract()[0]

        # 用urlretrieve(),下载图片验证码到本地项目
        try:
            urllib.request.urlretrieve(img_urls, 'D:/Py-Project/spider/bilbil_sel/yzm.png')
        except:
            pass

        time.sleep(3)

        """这里是对图片以文件的形式打开，主要是为了获取图片的大小"""
        # 对图片验证码进行提取,取图片标签
        img_label = self.browser.find_element_by_css_selector("img.geetest_item_img")

        # 获取点触图片链接
        src = img_label.get_attribute('src')

        # 获取图片二进制内容
        img_content = requests.get(src).content
        f = BytesIO()
        f.write(img_content)

        # 将图片以文件的形式打开，主要是为了获取图片的大小
        img0 = Image.open(f)

        # 获取图片与浏览器该标签大小的比例
        scale = [img_label.size['width'] / img0.size[0],
                 img_label.size['height'] / img0.size[1]]

        """对图片进行识别"""
        # 对接打码平台，识别验证码
        from bilbil_sel.parse_code import base64_api

        img_path = 'D:\\Py-Project\\spider\\bilbil_sel\\yzm.png'

        # 与接口对应
        code_result = base64_api(KUAI_USERNAME, KUAI_PASSWORD, img_path)
        print("验证码识别结果：", code_result)

        # 识别出来的坐标是用|隔开的，现在分隔一下
        result_list = code_result.split('|')

        position = [[int(j) for j in i.split(',')] for i in result_list]  # position = [[110,234],[145,247],[25,185]]
        for items in position:  # 模拟点击

            # 实现动作链,browser是浏览器的一个对象
            # move_to_element_with_offset()翻译是移动到带偏移的元素
            # img_label是图片的标签，也是验证码在登录时候的位置
            # perform()是执行整个鼠标动作链
            ActionChains(self.browser).move_to_element_with_offset(img_label, items[0] * scale[0],
                                                              items[1] * scale[1]).click().perform()
            time.sleep(1)

        # 点击确认
        self.browser.find_element_by_css_selector('div.geetest_commit_tip').click()
        time.sleep(3)
        try:
            # 点击登录
            self.browser.find_element_by_css_selector(".btn.btn-login").click()
        except:
            pass

        # 用户输入，阻塞浏览器关闭
        input()

        # 关闭浏览器
        self.browser.quit()

    def crack(self):
        """
        破解入口
        :return: None
        """
        self.input_open()
        self.pick_code()


if __name__ == "__main__":
    bilibili = BiliBiliLogin()
    bilibili.crack()









