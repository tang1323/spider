"""
爬取
解析
存储

这里是用线程池来实现的
这里的好处是每个表都能获取差不多一样的数量的数据
"""
import re
import ast
from urllib import parse  # 拼接url的
from datetime import datetime

import requests
from scrapy import Selector

from csdn_spider.models import *

domain = 'https://bbs.csdn.net/'


# 把放在js里面的代码获取下来，因为数据就放在里面
def get_notes_json():
    # 这里是获取json的一个文本，还要进一步提取
    left_menu_text = requests.get("https://bbs.csdn.net/dynamic_js/left_menu.js?csdn").text

    # search是可以从任意地方开始，哪怕回车换行符都会去匹配
    # 如果是match的话就从第一行开始
    """
    (.*?])这个是取到第一个]就结束了
    (.*])是匹配最后一个]才结束
    """
    nodes_str_match = re.search("forumNodes: (.*])", left_menu_text)
    if nodes_str_match:
        # 在要爬取的js里有"null"，python里的json会抛异常的，这里所以要更换成一个None
        nodes_str = nodes_str_match.group(1).replace("null", "None")
        # ast.literal_eval转换成list
        nodes_list = ast.literal_eval(nodes_str)
        return nodes_list
    # 如果遇到反爬，那就返回一个空列表
    return []


# 将js的格式提取出url到list中
url_list = []


def process_nodes_list(nodes_list):
    for item in nodes_list:
        if "url" in item:
            # item的url不为空才放进来
            if item["url"]:
                url_list.append(item["url"])

            # 有的还有children文件
            if "children" in item:
                # 这再提取这个children
                process_nodes_list(item["children"])


# 我们获取第一个层url就行了
def get_level1_list(nodes_list):
    # 这是第一层的url
    level1_url = []
    for item in nodes_list:
        # item的url不为空才放进来
        if "url" in item and item["url"]:
            # item的url不为空才放进来
            level1_url.append(item["url"])

    return level1_url


# 获取最终需要爬取的url
def get_last_urls():
    nodes_list = get_notes_json()
    process_nodes_list(nodes_list)
    # level1_url是第一层url
    level1_url = get_level1_list(nodes_list)
    last_url = []
    for url in url_list:
        # 把不是第一层的url放在last_url里面
        if url not in level1_url:
            last_url.append(url)

    # 这是爬取精华与完结的url，这是拼url
    all_urls = []
    for url in last_url:
        # 用parse.urljoin拼接域名
        all_urls.append(parse.urljoin(domain, url))
        all_urls.append(parse.urljoin(domain, url + "/recommend"))
        all_urls.append(parse.urljoin(domain, url + "/closed"))
    return all_urls


# 这是帖子的详情页面提取以及回复提取
def parse_topic(url):
    print("解析帖子页面：{}".format(url))
    topic_id = url.split("/")[-1]

    # 获取一下传递进来的值
    res_text = requests.get(url, cookies=cookie_dict).text

    # 做成一个选择器，这样可以用selector选择器提取数据
    sel = Selector(text=res_text)

    # 获取出所有关于内容和回答的文本， 这是第一个div的，是topic的
    all_divs = sel.xpath("//div[starts-with(@id, 'post-')]")

    # 第一个的内容就是作者的文章
    topic_item = all_divs[0]
    topic = Topic()
    # 内容
    content = topic_item.xpath(".//div[@class='text']/text()").extract()[0]

    # 点赞数量, 这里取的是'点赞1'这种类型的，所以要用re去掉点赞
    praised_nums = topic_item.xpath(".//label[@class='red_praise digg d_hide']//em/text()").extract()[0]
    praised_match = re.search(".*?(\d+)", praised_nums)
    if praised_match:
        praised_num = int(praised_match.group(1))
        topic.praised_nums = int(praised_num)
        topic.praised_num = praised_num
    else:
        praised_nums = 0
        topic.praised_nums = int(praised_nums)
        topic.praised_nums = praised_nums

    # 结帖率
    jtl_str = topic_item.xpath(".//div[@class='close_topic']/text()").extract()[0]

    # 开始先设置为0
    jtl = 0
    # 结帖的数字
    jtl_match = re.search("(\d+)", jtl_str)
    if jtl_match:
        jtl = int(jtl_match.group(1))

    """
    这是保存在topic中的
    """
    # 在这里做一个判断,看看id这个值是否相等
    existed_topics = Topic.select().where(Topic.id == topic_id)

    # 如果id不存在的话，那就用force_insert做一个插入的操作，不然没有错误也进不了库
    if existed_topics:
        # 获取第1个元素
        topic = existed_topics[0]

        # 保存相应的字段
        topic.content = content
        topic.jtl = jtl
        topic.save()

    # 从第2 个开始就是用户评论的， 所以从1开始
    all_answer_url = all_divs[1:]
    # return answer_list(all_answer_url, topic_id, sel)
    # 交给线程池运行控制
    return executor.submit(answer_list, all_answer_url, topic_id, sel)


# 这是用户回帖的字段
def answer_list(url, answer_topic_id, sel_re):
    # answer_url_list = re.search(".*(\?.+=).*", url)

    # 如果是用户回复第二页的话，url里面就有?page=,然后才能执行这里的语句
    if "?page=" in url:
        print("解析帖子回复页面：{}".format(url))
        # 获取一下传递进来的值
        res_text_answer = requests.get(url, cookies=cookie_dict).text

        # 做成一个选择器，这样可以用selector选择器提取数据
        sel_re = Selector(text=res_text_answer)

        # 获取出所有关于内容和回答的文本， 这是第一个div的，是topic的
        all_answer_divs = sel_re.xpath("//div[starts-with(@id, 'post-')]")

        # 因为回复的第二页是从第一个就是，所以从0开始取
        answer_item_re = all_answer_divs[0:]

        for answer_item in answer_item_re:
            """
            这是第二页面以后的回复
            """

            answer = Answer()
            answer.topic_id = answer_topic_id

            # 获取作者的信息
            author_info = answer_item.xpath(".//div[@class='nick_name']//a[1]/@href").extract()[0]

            # 获取作者的id，在href最后的就是https://blog.csdn.net/qq_37449342
            author_id = author_info.split("/")[-1]

            # 时间
            create_time = answer_item.xpath(".//label[@class='date_time']/text()").extract()[0]
            # 转换格式
            create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")

            # 回答answer进入数据库
            answer.author = author_id
            answer.create_time = create_time

            # 点赞数量
            praised_nums = answer_item.xpath(".//label[@class='red_praise digg d_hide']/em/text()").extract()[0]
            praised_match = re.search(".*?(\d+)", praised_nums)
            if praised_match:
                praised_num = int(praised_match.group(1))
                answer.praised_nums = int(praised_num)
            else:
                praised_nums = 0
                answer.praised_nums = int(praised_nums)

            # 回答的内容
            content = answer_item.xpath(".//div[@class='post_body post_body_min_h']/text()").extract()[0]
            answer.content = content

            answer.save()

    # 否则的话就可以直接从parse_topic()方法拿过来的selector,做解析字段
    else:
        # answer_item = url
        # 这是第二个div，是其他用户的回答answer
        """
        这是保存到answer表中的字段,这是第一页的回复
        """
        for answer_item in url:
            answer = Answer()
            answer.topic_id = answer_topic_id

            # 获取作者的信息
            author_info = answer_item.xpath(".//div[@class='nick_name']//a[1]/@href").extract()[0]

            # 获取作者的id，在href最后的就是https://blog.csdn.net/qq_37449342
            author_id = author_info.split("/")[-1]

            # 时间
            create_time = answer_item.xpath(".//label[@class='date_time']/text()").extract()[0]
            # 转换格式
            create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")

            # 回答answer进入数据库
            answer.author = author_id
            answer.create_time = create_time

            # 点赞数量
            praised_nums = answer_item.xpath(".//label[@class='red_praise digg d_hide']/em/text()").extract()[0]
            praised_match = re.search(".*?(\d+)", praised_nums)
            if praised_match:
                praised_num = int(praised_match.group(1))
                answer.praised_nums = int(praised_num)
            else:
                praised_nums = 0
                answer.praised_nums = int(praised_nums)

            # 回答的内容
            content = answer_item.xpath(".//div[@class='post_body post_body_min_h']/text()").extract()[0]
            answer.content = content

            answer.save()

    # 下一页的爬取,必须不能为空才能用[0]，所以做一层判断
    # 有一些火热的帖子有很多回复，在这里要做下一页的逻辑
    # 这个sel_re是第二页的sel_re，不能是从parse_topic()上拿下来的sel，因为点击下一页得是新的一页

    next_page = sel_re.xpath("//a[@class='pageliststy next_page']/@href").extract()
    if next_page:
        # 进入下一页
        next_url = parse.urljoin(domain, next_page[0])

        # 又回到answer_list()解析
        # answer_list(next_url, answer_topic_id, sel_re)
        # 这里用线程池来控制
        executor.submit(answer_list, next_url, answer_topic_id, sel_re)



# 获取用户的详情
def parse_author(url):
    print("解析用户的详情页面：{}".format(url))
    author_id = url.split("/")[-1]

    headers = {
        "user-agent": 'Mozilla / 5.0(WindowsNT10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 80.0.3987.163Safari / 537.36Edg / 80.0.361.111'
    }

    # 获取一下传递进来的值
    res_text_answer = requests.get(url, cookies=cookie_dict, headers=headers).text

    # 做成一个选择器，这样可以用selector选择器提取数据
    sel = Selector(text=res_text_answer)

    # 找到总的位置,分别是两个
    url_all_list = sel.xpath(".//div[@class='data-info d-flex item-tiling']/dl/a/dt/span/text()").extract()
    # [79,10,2]
    active_all_list = sel.xpath(".//div[@class='data-info d-flex item-tiling']/dl/dt/span/text()").extract()
    # [31,3722, 239, 11, 121, 13]

    # 原创数
    original_nums = int(url_all_list[0])
    # 周排名
    week_rate = url_all_list[1]
    # 总排名
    all_rate = url_all_list[2]

    # 点击数量就是访问人数
    click_num = active_all_list[0]

    # 积分数
    integral_nums = int(active_all_list[1])

    # 粉丝数
    follower_nums = active_all_list[2]

    # 获赞数
    praised_nums = int(active_all_list[3])

    # 评论数
    answer_nums = int(active_all_list[4])

    # 收藏数
    collection_nums = int(active_all_list[5])

    # 用户的昵称
    name = sel.xpath(".//div[@class='profile-intro-name-boxTop']/a/span/text()").extract()[0]

    work_years = sel.xpath(".//div[@class='profile-intro-name-boxFooter']/span/text()").extract()[0]

    # 与models的orm眏射，保存到数据库中
    author = Author()
    author.id = author_id
    author.original_nums = original_nums
    author.week_rate = week_rate
    author.all_rate = all_rate
    author.click_num = click_num
    author.integral_nums = integral_nums
    author.follower_nums = follower_nums
    author.praised_nums = praised_nums
    author.answer_nums = answer_nums
    author.collection_nums = collection_nums
    author.name = name
    author.work_years = work_years

    # 先查询一下这个用记是否存在，再做插入保存
    existed_author = Author.select().where(Author.id == author_id)

    # 如果id不存在的话，那就用force_insert做一个插入的操作，不然没有错误也进不了库
    if existed_author:
        author.save()
    else:
        author.save(force_insert=True)


# 这里先在论坛首页获取列表url(获取的url交给parse_topic()方法处理)和一些字段信息
def parse_list(url):
    print("解析列表页：{}".format(url))
    res_text = requests.get(url, cookies=cookie_dict).text
    # 获取到这个列表的文本信息
    sel = Selector(text=res_text)

    # 获取到列表这个帖子,从下标第2个tr开始
    all_trs = sel.xpath("//table[@class='forums_tab_table']/tbody//tr")[2:]
    for tr in all_trs:
        """
        在这里如果不加.
        那在这里虽然做了遍历，但其实是//table[@class='forums_tab_table']//tr//td[1]/span/text()
        这样取的，也就是把所以的取出来，所以得加一个.
        .是代表当前一个

        为 什么要做if判断，因为[0]必须有数据才能取，不然会有异常
        """
        topic = Topic()
        if tr.xpath(".//td[1]/span/text()").extract():
            # 是否完结
            status = tr.xpath(".//td[1]/span/text()").extract()[0]
            topic.status = status

        if tr.xpath(".//td[2]/em/text()").extract():
            # 赏分
            score = tr.xpath(".//td[2]/em/text()").extract()[0]
            topic.score = int(score)

        # 帖子的url,因为之后还要对帖子进行爬取, 拼接url
        if len(tr.xpath(".//td[3]/a[1]/@href").extract()) == 2:
            topic_url = parse.urljoin(domain, tr.xpath(".//td[3]/a[1]/@href").extract()[1])
        else:
            topic_url = parse.urljoin(domain, tr.xpath(".//td[3]/a[1]/@href").extract()[0])

        # 帖子标题
        topic_title = tr.xpath(".//td[3]/a/text()").extract()[0]

        # 获取用户url
        author_url = parse.urljoin(domain, tr.xpath(".//td[4]/a/@href").extract()[0])

        # 获取用户的id，放在href最后面的就是
        author_id = author_url.split("/")[-1]

        # 创建时间
        create_time_str = tr.xpath(".//td[4]/em/text()").extract()[0]
        # 转换下格式
        create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M")

        # 回复查看的数量
        answer_info = tr.xpath(".//td[5]/span/text()").extract()[0]

        # 回复的数量
        answer_nums = answer_info.split("/")[0]

        # 查看的数量
        click_nums = answer_info.split("/")[1]

        # 最后的回复时间
        last_time_str = tr.xpath(".//td[6]/em/text()").extract()[0]
        # 转换下格式
        last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M")

        # 取帖子的的url后面的id
        topic.id = int(topic_url.split("/")[-1])

        # 存储到Topic()里
        topic.title = topic_title
        topic.author = author_id
        topic.click_num = int(click_nums)
        topic.answer_nums = int(answer_nums)
        topic.create_time = create_time
        topic.last_answer_time = last_time

        # 在这里做一个判断,看看id这个值是否相等
        existed_topics = Topic.select().where(Topic.id == topic.id)

        # 如果id不存在的话，那就用force_insert做一个插入的操作，不然没有错误也进不了库
        if existed_topics:
            topic.save()
        else:
            topic.save(force_insert=True)

        # 把分析下来的帖子详情url传给这个函数进一步解析
        # parse_topic(topic_url)
        # 这里交给线程池里发放任务
        executor.submit(parse_topic, topic_url)

        # 把分析下来的用户url传给这个函数进一步解析
        # parse_author(author_url)
        # 这里交给线程池里发放任务
        executor.submit(parse_author, author_url)

    # 下一页的爬取,必须不能为空才能用[0]，所以做一层判断
    next_page = sel.xpath("//a[@class='pageliststy next_page']/@href").extract()
    if next_page:
        # 进入下一页
        next_url = parse.urljoin(domain, next_page[0])

        # 又回到parse_list()解析
        # parse_list(next_url)
        # 交给线程池运行控制
        executor.submit(parse_list, next_url)


if __name__ == "__main__":
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


    from concurrent.futures import ThreadPoolExecutor


    # 这里控制并发10个
    executor = ThreadPoolExecutor(max_workers=10)
    # 开始程序
    last_urls = get_last_urls()
    for url in last_urls:
        # 现在是将我们的任务发放, 这里的url是要这样写的(具体看submit这个函数)
        executor.submit(parse_list, url)
        parse_list(url)

    """
    为什么爬取的时候author没有数据呢，
    因为这里ThreadPoolExecutor的队列是有先后顺序的
    先把executor.submit(parse_list, url)的全爬取完再来获取executor.submit(parse_topic, topic_url)
    
    """




















