

import requests
from scrapy import Selector
import csv

url = "https://cs.lianjia.com/ershoufang/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111"
}
response = requests.get(url=url, headers=headers).text
sel_css = Selector(text=response)
# print(sel)

# html_data = response.text
# print(html_data)
# 获取总的列表
sel = sel_css.css(".clear.LOGCLICKDATA")

for se in sel:

    # 房子标题
    title = se.css(".info.clear .title a::text").extract()[0]

    # 房子url
    url_detail = se.css(".info.clear .title a::attr(href)").extract()[0]

    # 房子地址
    addr = se.css(".positionInfo a::text").extract()
    addre = "- ".join(addr)

    # 房子介绍
    address = se.css(".address .houseInfo ::text").extract()[0]

    # 房子关注
    follow = se.css(".followInfo ::text").extract()[0]

    # 房子标签
    tags = se.css(".tag span::text").extract()

    # 房子价格
    price = se.css(".priceInfo .totalPrice span::text").extract()
    a = ["万元"]
    price_wy = price + a
    price_jo = "".join(price_wy)

    # 房子单价
    unitprice = se.css(".unitPrice span::text").extract()
    # print(title, url_detail, addre, address, follow, tags, price_jo, unitprice, sep="--")

    # mode="a"是以追加的方式写入， newline=""因为 保存csv它默认有个空行，通过newline来解决
    with open("链家二手房.csv", mode="a", encoding="utf-8", newline="") as f:
        # 传入一个文件对象f
        # 用csv_writer一个变量去接收一个csv的一个对象f
        csv_writer = csv.writer(f)
        # writerow()是以 一行一行的定入数据
        # 写入数据要有一个容器，写入哪些由自己决定
        csv_writer.writerow([title, url_detail, addre, address, follow, tags, price_jo, unitprice])




















