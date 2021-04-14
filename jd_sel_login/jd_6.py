
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

# 京东的帐号和密码
USERNAME = '13232732408'
PASSWORD = 'tangming960713'

# 快识别打码的平台
KUAI_USERNAME = 'tang1323'
KUAI_PASSWORD = '130796abc'
KUAI_SOFT_ID = 907581
KUAI_KIND = 9004


class JDLogin():
    # 初始化
    def __init__(self):
        self.url = 'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F'
        chrome_options = Options()  # 实例化这个Options(),要在webdriver.Chrome加上参数
        chrome_options.add_argument("--headless")  # 这个就是无界面启动selenium，一定要写的
        chrome_options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
        self.browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
        self.browser.maximize_window()  # 最大化浏览器
        self.username = USERNAME
        self.password = PASSWORD



    def input_open(self):

        login_success = False
        while not login_success:
            """
            打开网页输入用户名密码
            :return: None
            """
            self.browser.get(self.url)
            # 点击帐号登录
            self.browser.find_element_by_xpath('.//div[@class="login-tab login-tab-r"]/a[@clstag="pageclick|keycount|login_pc_201804112|10"]').click()
            time.sleep(0.5)


            # 输入帐号密码
            user = self.browser.find_element_by_css_selector(".itxt")
            password = self.browser.find_element_by_css_selector(".itxt.itxt-error")
            user.send_keys(self.username)
            time.sleep(0.5)
            password.send_keys(self.password)

            # 点击登录
            login_btn = self.browser.find_element_by_css_selector(".btn-img.btn-entry")
            # 随机暂停几秒
            time.sleep(random.random() * 3)
            # 点击登陆按钮
            login_btn.click()
            time.sleep(2)

            backimgUrl = self.browser.find_element_by_xpath(r'//div/div[@class="JDJRV-bigimg"]/img').get_attribute(
                "src")  # 背景缺口图链接
            gapUrl = self.browser.find_element_by_xpath(r'//div/div[@class="JDJRV-smallimg"]/img').get_attribute(
                "src")  # 块状缺口链接

            # 用urlretrieve(),下载图片验证码到本地项目
            urllib.request.urlretrieve(backimgUrl, "jd_6_cap.png")
            urllib.request.urlretrieve(gapUrl, "jd_6_gap.png")

            # 快识别打码的平台
            KUAI_USERNAME = 'tang1323'
            KUAI_PASSWORD = '130796abc'
            KUAI_SOFT_ID = 907581
            KUAI_KIND = 9004
            # 对接打码平台，识别验证码,这是快识别平台
            from jd_sel_login.parse_code import base64_api

            img_path = 'D:\\Py-Project\\spider\\jd_sel_login\\jd_6_cap.png'
            # img_path2 = 'D:\\Py-Project\\spider\\jd_sel_login\\jd_6_gap.png'
            # 与接口对应
            # 这里超级鹰只能识别图片的二进制，而快识别只识别原图片
            code_result = base64_api(KUAI_USERNAME, KUAI_PASSWORD, img_path)
            # print(type(code_result))
            print("验证码识别结果：", code_result)
            code = float(code_result) - 32
            print("转化之后的偏移值：", code)

            track = []  # 移动轨迹, 就是在滑动的这期间每一刻都是不一样的
            current = 0  # 当前位移
            # 减速阈值
            mid = code * 3 / 4  # code就是要移动的像素点，前4/5段加速 后1/5段减速
            t = 0.1  # 计算间隔
            v = 0  # 初速度
            while current < code:
                if current < mid:
                    # a = 3  # 加速度为+3
                    a = random.randint(2, 3)
                else:
                    # a = -3  # 加速度为-3
                    a = -random.randint(6, 7)
                v0 = v  # 初速度v0
                v = v0 + a * t  # 当前速度
                move = v0 * t + 1 / 2 * a * t * t  # 移动距离
                current += move  # 当前位移

                # if 0.6 < current - code < 1:
                #     move = move - 0.53
                #     track.append(round(move, 2))
                #
                # elif 1 < current - code < 1.5:
                #     move = move - 1.4
                #     track.append(round(move, 2))
                # elif 1.5 < current - code < 3:
                #     move = move - 1.8
                #     track.append(round(move, 2))
                #
                # else:
                #     track.append(round(move, 2))

                track.append(round(move))  # 加入轨迹
            return track

    def move_slider(self, track):
        slider = self.browser.find_elements_by_xpath(r'//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')[0]
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:  # 只有水平方向有运动 按轨迹移动
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()  # 松开鼠标
        time.sleep(5)


    def main(self):
        # 运行这个函数会返回一个列表，在input_open里是track
        # 然后现在传给gap
        gap = self.input_open()
        print("要移动的轨迹：", gap)
        self.move_slider(gap)
        input()
        self.browser.quit()


if __name__ == "__main__":
    jd = JDLogin()
    jd.main()















