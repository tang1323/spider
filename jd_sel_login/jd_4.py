

from collections import Counter
from PIL import Image
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains


class JDlogin():
    def __init__(self):#定义函数，链接登录页面
        self.driver = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")#启动调试工具
        self.driver.get('https://passport.jd.com/new/login.aspx')#获取JD登陆页面
        time.sleep(2)

    def get_picture(self):  # 获取图片
        self.driver.maximize_window()
        # 通过xpath寻找按键点击“账户登陆”
        self.driver.find_element_by_xpath('.//div[@class="login-tab login-tab-r"]/a').click()
        time.sleep(1)
        # 定位账号输入框
        self.driver.find_element_by_xpath('.//input[@id="loginname"]').send_keys('13232732408')
        time.sleep(1)
        # 定位密码输入框
        self.driver.find_element_by_xpath('.//input[@id="nloginpwd"]').send_keys('tangming960713')
        time.sleep(1)
        # 定位登陆按钮，并点击，此时会展示出验证码图片
        self.driver.find_element_by_xpath('.//div[@class="login-btn"]/a').click()
        time.sleep(1)
        # 通过修改JS隐藏滑块并截屏获取验证码图片，保存至当前目录，名为slice.png（双层图也是这么干，不过ClassName与xpath需要改动）
        js = 'document.getElementsByClassName("JDJRV-smallimg")[0].style.display="none"'
        self.driver.execute_script(js)
        slice_path = './slice.png'
        self.driver.find_element_by_xpath('.//div[@class="JDJRV-bigimg"]').screenshot(slice_path)
        time.sleep(1)
        # 停止1秒后恢复JS改动，回到页面最初状态（双层图亦然）
        js = 'document.getElementsByClassName("JDJRV-smallimg")[0].style.display="block"'
        self.driver.execute_script(js)

    def shape(self, w, h, image):  # 二值化，将所有的点位，全部换成0或255
        tem = 0
        for x in range(w):
            for y in range(h):
                tem += image.getpixel((x, y))
        pixel_ave = tem / w / h * 0.7
        for x in range(w):
            for y in range(h):
                p = image.getpixel((x, y))
                if p < pixel_ave:
                    image.putpixel((x, y), 0)
                else:
                    image.putpixel((x, y), 255)
        return image

    def reducenoise(self, image):  # 降噪处理
        w, h = image.size
        for x in range(0, 40):  # 处理最左边
            for y in range(h):
                image2 = image.putpixel((x, y), 255)
        return image

    def make_picture(self):  # 处理图片，灰度化与二值化、降噪
        im = Image.open('slice.png')
        im2 = im.convert("L")
        w, h = im2.size
        im3 = self.shape(w, h, im2)
        im4 = self.reducenoise(im3)
        return im3

    def get_juli(self, image):  # 计算距离
        w, h = image.size
        ls = []
        for i in range(31, w - 31):  # 图片最左边放置滑块，缺口坐标x不可能小于31
            for j in range(10, h):
                if image.getpixel((i, j)) < 100:
                    count = 0
                    for k in range(i, i + 31):
                        if image.getpixel((k, j)) < 100:
                            count += 1
                        else:
                            break
                    if count > 27: ls.append(i)

        return Counter(ls).most_common(1)[0][0]

    def get_track(self, distance):  # 设计拖动轨迹
        ls = [1]
        while 1:
            i = ls[-1] * 2
            ls.append(i)
            if sum(ls) > distance * 0.7:
                break

        ls.append(int(distance - sum(ls)))

        return ls

    def drog_btn(self, track):  # 拖动滑块
        # 定位滑块
        ele = self.driver.find_element_by_xpath('.//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')
        # 设计拖动动作链（点击且不放）
        ActionChains(self.driver).click_and_hold(ele).perform()
        # 根据设计的轨迹，实现滑块拖动
        for i in track:
            ActionChains(self.driver).move_by_offset(i, 0).perform()
        # 睡眠0.25秒，伪装成人的判断过程
        time.sleep(0.25)
        # 释放滑块，类似于松开鼠标
        ActionChains(self.driver).release().perform()
        time.sleep(2)

    def check(self):  # 再次尝试
        self.get_picture()
        image = self.make_picture()
        distance = self.get_juli(image)
        track = self.get_track(distance)
        self.drog_btn(track)


if __name__ == '__main__':
    login = JDlogin()
    login.get_picture()
    image = login.make_picture()
    distance = login.get_juli(image)
    track = login.get_track(distance)
    login.drog_btn(track)
    time_int = 0
    while time_int < 5:
        input("是否需要再次尝试")
        login.driver.refresh()
        login.check()
        time_int += 1











