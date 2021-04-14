from peewee import *

db = MySQLDatabase('spider', host="127.0.0.1", port=3306, user="tangming", password='130796')


# 这个是共用的类
class BaseModel(Model):
    class Meta:
        database = db



# 设计数据表的时候有几个重要点一定要注意
"""
char类型：要设置最大长度，一般是255，也可以自定义
对于无法确定最大长度的字段，可以设置为Text
设计表的时候， 采集到的数据要尽量先做格式化处理
default和null=True,null默认是不能为空的，如果有时候不确定，那就设置成null=True
default如果在一定情况下没有数据的话，那就设置成default=0
"""


# 主题的表结构设计
class Topic(BaseModel):
    # 标题
    title = CharField()

    # 内容
    content = TextField(default="")

    # csdn_id这是url上的一个id，不是简单的字符类型,这是主键
    id = IntegerField(primary_key=True)

    # 每个用户都有一个id，这个是字符串类型的
    author = CharField()

    # 创建时间
    create_time = DateTimeField()

    # 回复的数量
    answer_nums = IntegerField(default=0)

    # 点击数量
    click_num = IntegerField(default=0)

    # 点赞数量
    praised_nums = IntegerField(default=0)

    # 结贴率
    jtl = FloatField(default=0.0)

    # 赏分
    score = IntegerField(default=0)

    # 状态
    status = CharField()

    # 最后的回复时间
    last_answer_time = DateTimeField()


# 回答的提取字段
class Answer(BaseModel):
    # 这个是有多个回答的，是不有做主键，我们用默认的id来做主键相对合适一些
    topic_id = IntegerField()

    # 作者
    author = CharField()

    # 回复的内容
    content = TextField(default="")

    # 回复的时间
    create_time = DateTimeField()

    # 点赞的数量
    praised_nums = IntegerField(default=0)


# 用户的信息字段定义
class Author(BaseModel):
    # 作者名
    name = CharField()

    # 主键
    id = CharField(primary_key=True)

    # 点击数量就是访问人数
    click_num = CharField()

    # 原创数
    original_nums = IntegerField(default=0)

    # 周排名
    week_rate = CharField()

    # 总排名
    all_rate = CharField()

    # 评论数
    answer_nums = IntegerField(default=0)

    # 获赞数
    praised_nums = IntegerField(default=0)

    # 工作年限
    work_years = CharField(null=True)

    # 收藏
    collection_nums = IntegerField(default=0)

    # 粉丝数
    follower_nums = CharField()

    # 积分数
    integral_nums = IntegerField(default=0)


if __name__ == "__main__":
    # 生成表结构
    db.create_tables([Author])









