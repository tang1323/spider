


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


class LagouLogin():
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

        """
        打开网页输入用户名密码
        :return: None
        """
        login_success = False
        while not login_success:
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

            # 去执行js的逻辑，相对来说js的逻辑比较强大,document.querySelectorAll是原生的js逻辑
            # 获取没有块状的验证码
            # 执行js改变css样式， 显示没有缺口的图！！！
            # self.browser.execute_script('document.getElementsByClassName("JDJRV-smallimg")[0].style.display="none"')
            #
            # # 截取的验证码
            # image1 = self.crop_image("captcha1.png")


            # self.browser.execute_script('document.querySelectorAll("JDJRV-smallimg")[0].style="display: none;"')

            # 执行js改变css样式， 显示有缺口的图！！！重点是这一步
            self.browser.execute_script('document.getElementsByClassName("JDJRV-smallimg")[0].style.display="block"')
            image2 = self.crop_image("captcha2.png")

            # 快识别打码的平台
            KUAI_USERNAME = 'tang1323'
            KUAI_PASSWORD = '130796abc'
            KUAI_SOFT_ID = 907581
            KUAI_KIND = 9004
            # 对接打码平台，识别验证码,这是快识别平台
            from jd_sel_login.parse_code import base64_api

            img_path = 'D:\\Py-Project\\spider\\jd_sel_login\\captcha2.png'
            # img_path2 = 'D:\\Py-Project\\spider\\jd_sel_login\\jd_6_gap.png'
            # 与接口对应
            # 这里超级鹰只能识别图片的二进制，而快识别只识别原图片
            code_result = base64_api(KUAI_USERNAME, KUAI_PASSWORD, img_path)
            # print(type(code_result))
            print("验证码识别结果：", code_result)
            code = float(code_result) + 2
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

            slider = self.browser.find_elements_by_xpath(r'//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')[0]
            ActionChains(self.browser).click_and_hold(slider).perform()
            for x in track:  # 只有水平方向有运动 按轨迹移动
                ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).release().perform()  # 松开鼠标
            time.sleep(5)

            # if self.browser.find_element_by_css_selector(".nickname"):
            #     login_success = True

        Cookies = self.browser.get_cookies()
        # print(Cookies)
        print("登录成功，正在保存cookie到redis中.....")
        cookie_dict = {}

        for cookie in Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        self.browser.close()
        return cookie_dict




    def crop_image(self, image_file_name):
        # 定义一个文件的名称，也就是截图的文件保存成我们设置的文件名称
        # 截取验证码图片
        time.sleep(2)
        # 得到图片的元素
        img = self.browser.find_element_by_css_selector(".JDJRV-bigimg")
        # 这个图片的左上角的x,y坐标
        location = img.location
        print("图片的位置：", location)

        # 现在来得到这个图片的长和宽
        size = img.size

        top = location['y']     # 这是上边的横切面
        down = location['y'] + size["height"]   # 这是下边的横切面
        left = location["x"]    # 这是左边的横切面
        right = location['x'] + size["width"]   # 这是右边的横切面
        print("验证码截图的位置左切面left是：{0}，下切面top是：{1}，左切面right是：{2}，右切面down是：{3}：".format(left, top, right, down))

        # 获取整个屏幕的截图
        screen_shot = self.browser.get_screenshot_as_png()
        # 将screen_shot转换成一个Byte类型，然后用PIL下的Image转换成一个PL对象
        screen_shot = Image.open(BytesIO(screen_shot))
        # 得得整个屏幕的截图与验证码的坐标后，现在来做截图，参数是固定这么写的
        captcha = screen_shot.crop((int(left), int(top), int(right), int(down)))
        # 保存
        captcha.save(image_file_name)
        # 传出去
        return captcha

    def crack(self):
        """
        破解入口
        :return: None
        """
        cookie_dict = self.input_open()
        print(cookie_dict)
        # self.move_slider(gap)



        # self.pick_code()


if __name__ == "__main__":
    lagou = LagouLogin()
    lagou.crack()

































