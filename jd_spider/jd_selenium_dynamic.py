
"""
这里不再像静态网页那样获取
而是通过selenium加载后的网页，已经渲染的网页来获取数据
"""
import re
import time
import json
from datetime import datetime
from selenium import webdriver
from scrapy import Selector
from urllib import parse
from selenium.webdriver.chrome.options import Options   # 这是无界面启动selenium
from selenium.common.exceptions import NoSuchElementException   # 这是找不到某个元素面抛出的异常
from fake_useragent import UserAgent

from jd_spider.models import *


# 1.要想无界面启动selenium，先设置headless模式
chrome_options = Options()  # 实例化这个Options(),要在webdriver.Chrome加上参数
# chrome_options.add_argument("--headless")   # 这个就是无界面启动selenium，一定要写的
chrome_options.add_argument("--disable-gpu")    # 谷歌文档提到需要加上这个属性来规避bug

# 2.设置selenium不加载图片, blink-settings=imagesEnabled=false是固定的
chrome_options.add_argument("blink-settings=imagesEnabled=false")


def process_value(num_str):
    """
    将字符串类型的数字转换成数字
    :param num_str:字符串类型的数字，数字中可能包含 "万"
    :return:成功返回数字，默认返回0
    """
    nums = 0
    # \d只取数字，+就是不管几个数字都取
    re_math = re.search("(\d+)", num_str)
    if re_math:
        nums = int(re_math.group(1))   # 只取第一个
        if "万" in num_str:
            nums *= 10000
    return nums


def parse_good(good_id):

    browser.get('https://item.jd.com/{}.html'.format(good_id))
    # page_source就是运行js完后的html网页
    sel = Selector(text=browser.page_source)

    # 提取商品的基本信息
    good = Good(id=good_id)

    # 商品的名称, 不用join就是一个列表，用了join就成了str类型，但是这里有回车换行符，所以用strip()去掉前后空格
    name = "".join(sel.xpath(".//div[@class='sku-name']/text()").extract()).strip()

    # 价格
    price = float("".join(sel.xpath(".//span[@class='price J-p-{}']/text()".format(good_id)).extract()).strip())

    # 商品详情
    detail = "".join(sel.xpath("//div[@class='detail']//div[@class='tab-con']").extract())

    # 商品的轮播图,这里是取图片的url，这里有多张图，得到的是一个list
    good_image = sel.xpath(".//div[@class='spec-list']//ul/li/img/@src").extract()

    # 这个是谁发货，是京东自营还是第三方商家, 这里先获取它的html内容，不获取文本
    """
    如果这个商家是京东，那就不可以点击，只有一个span标签
    如果有第三方店家，那就是一个a标签，是可以点击的
    """
    supplier_info = "".join(sel.xpath(".//div[@id='summary-service']").extract())

    # text = '<a href="http://mall.jd.com/index-881388.html" target="_blank" clstag="shangpin|keycount|product|bbtn" class="hl_red">京日达服饰专营店</a>'

    re_match = re.search('<a href="(.*?)"', supplier_info)
    if re_match:
        good.supplier = re_match.group(1)
        # print(re_match.group(1))
    else:
        good.supplier = "京东"





    # 保存商品的信息
    good.name = name
    good.price = price
    good.content = detail
    # 用json.dumps转换成字符串
    good.image_list = json.dumps(good_image)

    # 模拟点击规格和包装,这里有两种取的方法
    ggbz_ele = browser.find_element_by_xpath(".//div[@class='tab-main large']//li[contains(text(),'规格与包装')]").click()
    # ggbz_ele = browser.find_element_by_xpath(".//li[@clatag='shangpin|keycount|product|pcanshutab']").click()
    time.sleep(4)
    sel_ggbz = Selector(text=browser.page_source)

    # 规格包装要双重定位，因为这里点击商品介绍也是在tab-con，所以要向上定位一下
    ggbz_detail = "".join(sel_ggbz.xpath(".//div[@id='detail']/div[@class='tab-con']").extract())
    good.ggbz = ggbz_detail

    # 模拟点击商品评价后获取评价信息
    sppj_ele = browser.find_element_by_xpath(".//li[@clstag='shangpin|keycount|product|shangpinpingjia_1']").click()
    time.sleep(5)

    # 这个是点击后渲染出来的，和前面的不一样
    sel_good = Selector(text=browser.page_source)

    # 获取标签所有列表
    tag_list = sel_good.xpath(".//div[@class='tag-list tag-available']//span/text()").extract()

    # 好评率
    good_rate = int(sel_good.xpath(".//div[@class='percent-con']/text()").extract()[0])
    good.good_rate = good_rate

    # 全部评估信息, 因为'全部评价19万+'是分开的，这里先把这两个先一起来取出来
    summary_as = sel_good.xpath(".//ul[@class='filter-list']/li/a")
    for summary in summary_as:
        # 这里取了'全部评价'后
        name = summary.xpath("./text()").extract()[0]
        # 这里再取19万+
        nums = summary.xpath("./em/text()").extract()[0]
        # 因为有"万",所以拿到这个process_value方法里转换成int
        nums = process_value(nums)

        if name == "晒图":
            good.has_image_comment_nums = nums
        elif name == "视频晒单":
            good.has_video_comment_nums = nums
        elif name == "追评":
            good.has_add_comment_nums = nums
        elif name == "好评":
            good.well_comment_nums = nums
        elif name == "中评":
            good.middle_comment_nums = nums
        elif name == "差评":
            good.bad_comment_nums = nums
        elif name == "全部评价":
            good.comments_nums = nums

    # 保存商品信息，先查询有没有这个商品再做保存
    """
    为什么这个good.save()是一个外键写在summary.save()前面
    因为good是在另一张上是一个外键，在这里我们先必须先保存good这个商品，外键才开始有作用，不然会报错
    先保存主键，再保存外键(这是一个另一个表了)
    因为外键依赖主键， 这是主键，所以比summary写的早一些
    """
    existed_good = Good.select().where(Good.id == good_id)
    if existed_good:
        good.save()
    else:
        good.save(force_insert=True)

    # 这里做tag_list的保存，已经在71获取下来了，这里再for循环一下保存到另一张表的
    for tag in tag_list:
        # 流畅至极(79)这样两边的值都能取出来了
        # (.*)是取流畅至极， (\d+)是取(79)， \( \)是转义字符
        re_match = re.match("(.*)\((\d+)\)", tag)
        tag_name = re_match.group(1)
        nums = int(re_match.group(2))

        # 因为这里在models表里没有设计它的id，也就是说它有自己的id
        """
        那怎么才能支检测这个id是否存在，因为这个GoodEvaluateSummary是有个外键存在的
        所以我们拿这个外键去看看在主键在其它表检测是否存在
        """
        # 这是检测是否存在，也就是达到去重的逻辑
        existed_summarys = GoodEvaluateSummary.select().where(GoodEvaluateSummary.good == good, GoodEvaluateSummary.tag==tag_name)
        if existed_summarys:
            summary = existed_summarys[0]

        else:
            summary = GoodEvaluateSummary(good=good)

        """
        这是必须让good.save()先保存， 这是保存商品的信息，这是主键，我们这里有个字段是在GoodEvaluateSummary有外键的，所以先保存good
        再保存这个summary.save()，这是保存商品的评估信息，字段比较少
        因为外键依赖主键， 这是外键，所以比good写的晚一些
        """
        summary.tag = tag_name
        summary.num = nums
        summary.save()


    # 获取商品的评价
    # 这是默认有下一页的
    has_next_page = True
    while has_next_page:
        all_evaluate = sel_good.xpath(".//div[@class='comment-item']")
        for item in all_evaluate:
            good_evaluate = GoodEvaluate(good=good)

            # 每个评论都有一个id
            evaluate_id = item.xpath("./@data-guid").extract()[0]
            # 因为是无界面启动selenium，所以打印一下
            print(evaluate_id)
            good_evaluate.id = evaluate_id

            # 用户的头像url
            head_url = "http:"
            user_head_url = parse.urljoin(head_url, item.xpath(".//div[@class='user-info']//img/@src").extract()[0])
            # 用户名,使用join就不再后面加[0]
            user_name = "".join(item.xpath(".//div[@class='user-info']/text()").extract()).strip()

            good_evaluate.user_head_url = user_head_url
            good_evaluate.user_name = user_name

            # 评分是在comment-item下的第2个div中下的第1个div
            star = item.xpath("./div[2]/div[1]/@class").extract()[0]
            # 做一个转换，取最后一个
            star = int(star[-1])
            good_evaluate.star = star

            # 这个是评论内容
            evaluate = "".join(item.xpath("./div[2]/p[1]/text()").extract()).strip()
            good_evaluate.content = evaluate

            # 评论的图片url
            image_list = item.xpath("./div[2]//div[@class='pic-list J-pic-list']/a/img/@src").extract()
            # 评论视频的url
            video_list = item.xpath("./div[2]//div[@class='J-video-view-wrap clearfix']//video/@src").extract()



            # 用json.dumps转换成字符串
            good_evaluate.image_list = json.dumps(image_list)
            good_evaluate.video_list = json.dumps(video_list)

            # 用户这个评论还有人评论的数量
            comment_nums = int(item.xpath(".//div[@class='comment-op']/a[3]/text()").extract()[0])
            # 有人为这个用户点赞的数量
            praised_nums = int(item.xpath(".//div[@class='comment-op']/a[2]/text()").extract()[0])

            good_evaluate.praised_nums = praised_nums
            good_evaluate.comment_nums = comment_nums

            # 用户买的是商品信息
            comment_info = item.xpath(".//div[@class='order-info']/span/text()").extract()
            # 最后的时间值不要[::-1]是倒过来
            order_info = comment_info[:-1]
            # 这里放评论时间
            evaluate_time = comment_info[-1]
            evaluate_time = datetime.strptime(evaluate_time, "%Y-%m-%d %H:%M")

            good_evaluate.good_info = json.dumps(order_info)
            good_evaluate.evaluate_time = evaluate_time

            # 保存评价信息， 先查询是否存在，也是有id值的
            existed_good_evaluates = GoodEvaluate.select().where(GoodEvaluate.id==good_evaluate.id)
            if existed_good_evaluates:
                good_evaluate.save()
            else:
                good_evaluate.save(force_insert=True)

        try:
            next_page_ele = browser.find_element_by_xpath("//div[@id='comment']//a[@class='ui-pager-next']")
            # next_page_ele.click() # 这个键被其他组件挡住了
            next_page_ele.send_keys("\n")   # 平时回车键也能点击
            time.sleep(5)
            sel_good = Selector(text=browser.page_source)
        except NoSuchElementException as e:
            print(e)
            has_next_page = False


    browser.close()


if __name__ == "__main__":
    # chrome_options是无界面启动selenium

    browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe", chrome_options=chrome_options)
    # cookies = browser.get_cookies()
    # # 把cookies做一个转换
    # cookie_dict = {}
    # for item in cookies:
    #     cookie_dict[item['name']] = item["value"]

    # ua = UserAgent()
    # headers = {
    #     'User-Agent': ua.random
    # }
    # headers = {
    #     "User-Agent": ua.random
    # }

    parse_good(100016034400)


















