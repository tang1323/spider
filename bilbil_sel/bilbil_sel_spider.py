
"""这里是有截图的几种方式，也有bilibili的登录简单版本"""
from selenium import webdriver
import time
import requests
from io import BytesIO
from PIL import Image   # 这是安装pillow包，专门处理图像的
from selenium.webdriver import ActionChains     # 导入鼠标动作链对象
from scrapy import Selector
import urllib.request


# 创建一个浏览器对象
browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")

# 打开请求网页页面
browser.get('https://passport.bilibili.com/login')

# 浏览器渲染页面需要时间，隐式等待，sleep是强制等待
browser.implicitly_wait(2)

browser.maximize_window()   # 最大化浏览器

# 输入用户名
user_input = browser.find_element_by_css_selector("#login-username").send_keys("13232732408")
time.sleep(1)

# 输入密码
user_password = browser.find_element_by_css_selector("#login-passwd").send_keys("130796abc")
time.sleep(1)

# 点击登录按钮
button = browser.find_element_by_css_selector(".btn.btn-login").click()
time.sleep(1)

# ---------------------下载图片给快识别平台识别--------------------
# page_source就是运行js完后的html网页
sel_css = Selector(text=browser.page_source)


img_urls = sel_css.css(".geetest_item_wrap img::attr(src)").extract()[0]

# Image.open(BytesIO(img_urls))
# 下载图片验证码
urllib.request.urlretrieve(img_urls, 'D:\\Py-Project\\spider\\bilbil_sel\\yzm.png')

# ------------------------保存结束--------------------------

"""这里是对图片以文件的形式打开，主要是为了获取图片的大小"""
# 对图片验证码进行提取,取图片标签
img_label = browser.find_element_by_css_selector("img.geetest_item_img")
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


"""这是第二种截图方法"""
# 保存图片到当前项目目录下,screenshot翻译是截图,save_screenshot是截整个浏览页面
# browser.save_screenshot("big.png")

"""截图技术"""
# location是可以获取这个元素左上角坐标,就是验证码的左上顶点
# location = img_label.location
# print(location)
#
# # size可以获取这个元素的宽（width）和高（height）
# size = img_label.size
# print(size)
#
#
#
# # 计算验证码的左上右下模切面
# """因为location和size取的值小了，这里加上一些值才能截图"""
# left = location['x'] + 415  # 这是左边的横切面
# top = location['y'] + 130   # 这是上边的横切面
#
# a = size['width'] + 130
# b = size['height'] + 170
# right = left + a  # 这是右边的横切面
# down = top + b  # 这是下边的横切面
#
#
# """截图的第一种方法"""
# # get_screenshot_as_png是selenium的一种方法，获取截图
# screen_shot = browser.get_screenshot_as_png()
# BytesIO()是保存图片，图片就是二进制
# screen_shot = Image.open(BytesIO(screen_shot))
#
# """这是第二种截图方法"""
# # 打开我们截的整个图片
# # im = Image.open("big.png")
#
# # # crop()根据图片的左上右下横切面区域进行裁剪
# im = screen_shot.crop((int(left), int(top), int(right), int(down)))  # 对浏览器截图进行裁剪
# im.save("yzm.png")


# 对接打码平台，识别验证码
from bilbil_sel.parse_code import base64_api


img_path = 'D:\\Py-Project\\spider\\bilbil_sel\\yzm.png'
# 与接口对应
code_result = base64_api("tang1323", "130796abc", img_path)
print("验证码识别结果：", code_result)


# 识别出来的坐标是用|隔开的，现在分隔一下
result_list = code_result.split('|')

position = [[int(j) for j in i.split(',')] for i in result_list]  # position = [[110,234],[145,247],[25,185]]
for items in position:  # 模拟点击

    # 实现动作链,browser是浏览器的一个对象
    # move_to_element_with_offset()翻译是移动到带偏移的元素
    # img_label是图片的标签，也是验证码在登录时候的位置
    # perform()是执行整个鼠标动作链
    ActionChains(browser).move_to_element_with_offset(img_label, items[0]*scale[0], items[1]*scale[1]).click().perform()
    time.sleep(1)


# 点击确认
certern_btn = browser.find_element_by_css_selector('div.geetest_commit_tip')
certern_btn.click()

# 点出登录
btn_login = browser.find_element_by_css_selector(".btn.btn-login").click()

# 有多个xy坐标，在result_list中，用for循环点击每一个坐标
# for result in result_list:
#     # x和y中间是有逗号隔开的，现在切分一下，[0]取第一个就是x轴
#     x = result.split(',')[0]    # x,y都是是str类型
#     y = result.split(',')[1]
#     time.sleep(1)
#
#     # 实现动作链,browser是浏览器的一个对象
#     # move_to_element_with_offset()翻译是移动到带偏移的元素
#     # img_label是图片的标签，也是验证码在登录时候的位置
#     # perform()是执行整个鼠标动作链
#     ActionChains(browser).move_to_element_with_offset(img_label, x, y).click().perform()


input()     # 用户输入，阻塞浏览器关闭

# 关闭浏览器
browser.quit()



