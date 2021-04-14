
import random

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib import request
from time import sleep
import cv2
import numpy as np
from selenium.webdriver import ActionChains
from lxml.html import etree
from PIL import Image

import re, requests
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
# 设置无界面模式
from selenium.webdriver.chrome.options import Options


class JD_Login(object):
    def __init__(self):
        self.left = 31  # 定义一个左边的起点 缺口一般离图片左侧有一定的距离 有一个滑块
        self.url = 'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F'
        self.chromedriverPath = "D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=self.chromedriverPath)
        self.wait = WebDriverWait(self.driver, 20)  # 设置等待时间20秒
        self.username = "13232732408"
        self.password = "tangming960713"

    def agreement_inputPhone(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        sleep(1)
        # 点击账户登录
        self.driver.find_elements_by_xpath('//div[@class="login-tab login-tab-r"]//a')[0].click()
        sleep(3)
        self.inputuser = self.wait.until(EC.presence_of_element_located((By.NAME, "loginname")))
        self.inputuser.send_keys(self.username)
        self.inputpwd = self.wait.until(EC.presence_of_element_located((By.NAME, "nloginpwd")))
        self.inputpwd.send_keys(self.password)
        sleep(1)
        # 点击登录按钮,出现验证码图片
        login_button = self.driver.find_elements_by_xpath(r'//a[@id="loginsubmit"]')[0]
        login_button.click()
        sleep(3)  # 这里必须睡眠,不然会获取不到缺口图和缺口

    def get_image(self):
        backimgUrl = self.driver.find_element_by_xpath(r'//div/div[@class="JDJRV-bigimg"]/img').get_attribute("src")  # 背景缺口图链接
        gapUrl = self.driver.find_element_by_xpath(r'//div/div[@class="JDJRV-smallimg"]/img').get_attribute("src")  # 块状缺口链接

        # 用urlretrieve(),下载图片验证码到本地项目
        request.urlretrieve(backimgUrl, "backing.png")
        request.urlretrieve(gapUrl, "gap.png")

    def get_diff_location(self):
        # 获取图片并灰度化， 0就是黑白化
        block = cv2.imread("gap.png", 0)
        template = cv2.imread("backing.png", 0)

        # 二值化后的图片名称
        blockName = "block.jpg"
        templateName = "template.jpg"

        # 将二值化后的图片进行保存， 这里己经做好黑白化并保存了
        cv2.imwrite(blockName, block)
        cv2.imwrite(templateName, template)

        # 先读block.jpg这个图片
        block = cv2.imread(blockName)

        # cvtColor()彩色图像转为灰度图像
        block = cv2.cvtColor(block, cv2.COLOR_RGB2GRAY)

        block = abs(255 - block)
        cv2.imwrite(blockName, block)
        block = cv2.imread(blockName)
        template = cv2.imread(templateName)
        # 获取偏移量
        # 查找block在template中的位置，返回result是一个矩阵，是每个点的匹配结果

        result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
        print(result)
        x, y = np.unravel_index(result.argmax(), result.shape)
        print("x方向的偏移:", int(y * 0.4 + 18), 'x:', x, 'y:', y)
        return y


    def get_move_track(self, gap):
        print("需要移动的距离:" , gap)
        track = []  # 移动轨迹, 就是在滑动的这期间每一刻都是不一样的
        current = 0  # 当前位移
        # 减速阈值
        mid = gap * 3 / 4  # gap就是要移动的像素点，前4/5段加速 后1/5段减速
        t = 0.2  # 计算间隔
        v = 0  # 初速度
        while current < gap:
            if current < mid:
                # a = 3  # 加速度为+3
                a = random.randint(2, 3)
            else:
                # a = -3  # 加速度为-3
                a = - random.randint(6, 7)
            v0 = v  # 初速度v0
            v = v0 + a * t  # 当前速度
            move = v0 * t + 1 / 2 * a * t * t  # 移动距离
            current += move  # 当前位移

            if 0.6 < current - gap < 1:
                move = move - 0.53
                track.append(round(move, 2))

            elif 1 < current - gap < 1.5:
                move = move - 1.4
                track.append(round(move, 2))
            elif 1.5 < current - gap < 3:
                move = move - 1.8
                track.append(round(move, 2))

            else:
                track.append(round(move, 2))


            # track.append(round(move))  # 加入轨迹
        return track

    def move_slider(self, track):
        slider = self.driver.find_elements_by_xpath(r'//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')[0]
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:  # 只有水平方向有运动 按轨迹移动
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        sleep(1)
        ActionChains(self.driver).release().perform()  # 松开鼠标

    def main(self):
        self.agreement_inputPhone()
        self.get_image()
        gap = self.get_diff_location()
        track = self.get_move_track(gap)
        print("移动轨迹",track)
        self.move_slider(track)


if __name__ == "__main__":
    jd = JD_Login()
    jd.main()














