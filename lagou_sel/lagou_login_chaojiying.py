

import time
import random
import requests
from io import BytesIO
from PIL import Image   # 这是安装pillow包，专门处理图像的
from selenium.webdriver import ActionChains     # 导入鼠标动作链对象
from scrapy import Selector
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
"""这是用快识别打码平台的登录方式"""

# 拉勾的帐号和密码
USERNAME = '13232732408'
PASSWORD = 'tang130796'

# 快识别打码的平台
KUAI_USERNAME = 'tang1323'
KUAI_PASSWORD = '130796abc'
KUAI_SOFT_ID = 907581
KUAI_KIND = 9004


class LagouLogin():
    # 初始化
    def __init__(self):
        self.url = 'https://www.lagou.com/'
        chrome_options = Options()  # 实例化这个Options(),要在webdriver.Chrome加上参数
        chrome_options.add_argument("--headless")  # 这个就是无界面启动selenium，一定要写的
        chrome_options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
        self.browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
        self.browser.maximize_window()  # 最大化浏览器
        self.username = USERNAME
        self.password = PASSWORD



    def input_open(self):

        i = 0
        login_success = False
        while not login_success:
            """
            打开网页输入用户名密码
            :return: None
            """
            self.browser.get(self.url)
            if i == 0:
                i += 1
                # 选择城市
                self.browser.find_element_by_xpath('//*[@id="changeCityBox"]/ul/li[4]/a').click()
                time.sleep(0.5)

            # 点击登录
            self.browser.find_element_by_css_selector("ul.passport a.login").click()
            time.sleep(0.5)

            # 输入帐号密码
            user = self.browser.find_element_by_css_selector(".forms-top-block.forms-top-password input.input.login_enter_password.HtoC_JS")
            password = self.browser.find_element_by_css_selector(".forms-top-block.forms-top-password input[type='password']")
            user.send_keys(self.username)
            time.sleep(0.5)
            password.send_keys(self.password)

            # 点击登录
            login_btn = self.browser.find_element_by_css_selector(".login-btn.login-password.sense_login_password.btn-green")
            # 随机暂停几秒
            time.sleep(random.random() * 3)
            # 点击登陆按钮
            login_btn.click()
            time.sleep(2)

        # def pick_code(self):
            """保存图片到本地项目"""

            # page_source就是运行js完后的html网页
            sel_css = Selector(text=self.browser.page_source)

            # 这个和bilibili放在一样的路径下
            img_urls = sel_css.css(".geetest_item_wrap img::attr(src)").extract()[0]

            # 用urlretrieve(),下载图片验证码到本地项目
            try:
                urllib.request.urlretrieve(img_urls, 'D:/Py-Project/spider/lagou_sel/lagou_yzm.png')
            except:
                pass

            time.sleep(3)

            """这里是对图片以文件的形式打开，主要是为了获取图片的大小"""
            # 对图片验证码进行提取,取图片标签,geetest_table_box,geetest_item_img
            # 这个也跟bilibili一样，我在这里向上取一级
            img_label = self.browser.find_element_by_css_selector(".geetest_table_box img.geetest_item_img")

            """
            这个在拉勾可有可无
            但是拉勾有三种验证码，汉字点选和物体识别的图片是放在同样的路径下
            所以打开这个只是计算图片的大小而已
            """
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
            # ---------------------------------------------------------
            # 对接打码平台，识别验证码,这是快识别平台
            # from lagou_sel.parse_code import base64_api
            #
            # img_path = 'D:\\Py-Project\\spider\\lagou_sel\\lagou_yzm.png'
            # 与接口对应
            # 这里超级鹰只能识别图片的二进制，而快识别只识别原图片
            # code_result = base64_api(settings.KXB_USERNAME, settings.KXB_PASSWORD, img_path)
            # print("验证码识别结果：", code_result)
            #
            # # 识别出来的坐标是用|隔开的，现在分隔一下
            # result_list = code_result.split('|')
            # -----------------------------------------------------------------------------

            # ------------------------------------------------------------
            # 对接打码平台，识别验证码,这是超级鹰识别平台
            from tools.chaojiying import Chaojiying_Client
            CHAOJIYING_USERNAME = '1171242903'
            CHAOJIYING_PASSWORD = '130796abc'
            CHAOJIYING_SOFT_ID = 907581
            CHAOJIYING_KIND = 9004

            # 与接口对应
            cjy = Chaojiying_Client(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)
            # 这里超级鹰只能识别图片的二进制，而快识别只识别原图片
            result = cjy.PostPic(img_content, '9101')
            print(result)

            # 识别出来的坐标是用|隔开的，现在分隔一下
            result_list = result["pic_str"].split('|')
            # —---------------------------------------------------------------

            position = [[int(j) for j in i.split(',')] for i in result_list]  # position = [[110,234],[145,247],[25,185]]
            for items in position:  # 模拟点击
                print("正在点击{}".format(items))

                # 实现动作链,browser是浏览器的一个对象
                # move_to_element_with_offset()翻译是移动到带偏移的元素
                # img_label是图片的标签，也是验证码在登录时候的位置
                # perform()是执行整个鼠标动作链
                ActionChains(self.browser).move_to_element_with_offset(img_label, items[0]*scale[0],
                                                                  items[1]*scale[1]).click().perform()
                time.sleep(1)

            # 点击确认
            self.browser.find_element_by_css_selector('div.geetest_commit_tip').click()
            time.sleep(3)
            # 点击登录
            try:
                self.browser.find_element_by_css_selector(".login-btn.login-password.sense_login_password.btn-green").click()
                print("登录成功")
            except:
                pass

            time.sleep(3)
            # page_source就是运行js完后的html网页
            # res_css = Selector(text=browser.page_source)
            # return res_css

            try:
                self.browser.find_element_by_css_selector('.unick')
                # sel_css.css('.unick')
                login_success = True
            except:
                pass
        # 用get_cookies()获取cookies,变里获取的是一个对象
        Cookies = self.browser.get_cookies()
        print("保存cookies到redis中。。。")
        cookie_dict = {}

        for cookie in Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        self.browser.quit()
        return cookie_dict

    def crack(self):
        """
        破解入口
        :return: None
        """
        self.input_open()
        # self.pick_code()


if __name__ == "__main__":
    lagou = LagouLogin()
    lagou.crack()






























