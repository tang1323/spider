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
表结构一定要设计好
"""


# 这是商品的基本信息
class Good(BaseModel):
    # 这是主键，primary_key=True是要去重的，这个id 是京东https://item.jd.com/100016034400.html后的100016034400
    # 要多分析哪些是id，这很重要
    id = IntegerField(primary_key=True, verbose_name="商品id")

    name = CharField(max_length=500, verbose_name="商品名称")

    content = TextField(default="", verbose_name="商品描述")

    # 这是京东自营的还是商家自营的
    supplier = CharField(max_length=500, default="")
    ggbz = TextField(default="", verbose_name="规格和包装")

    # 这个是商品的轮播图，在这里明明是一对多的关系，为什么不再设计一张表？
    # 因为这是考虑到存储效率和读取效率，我们这里只是进行一个保存，并不进一步的操作，所以保存在这里是很合适 的
    # 在这里只做一个序列化的一个字符串，所以是一个TextField
    image_list = TextField(default="", verbose_name="商品轮播图")
    price = FloatField(default=0.0, verbose_name="商品价格")

    good_rate = IntegerField(default=0, verbose_name="好评率")
    comments_nums = IntegerField(default=0, verbose_name="评论数")
    has_image_comment_nums = IntegerField(default=0, verbose_name="晒图数")
    has_video_comment_nums = IntegerField(default=0, verbose_name="视频晒单数")
    has_add_comment_nums = IntegerField(default=0, verbose_name="追评数")
    well_comment_nums = IntegerField(default=0, verbose_name="好评数")
    middle_comment_nums = IntegerField(default=0, verbose_name="中评数")
    bad_comment_nums = IntegerField(default=0, verbose_name="差评数")


# 这是商品的评估的具体信息
class GoodEvaluate(BaseModel):
    id = CharField(primary_key=True)
    # 这个Good是说属于哪个商品的评论，这是一个外键
    good = ForeignKeyField(Good, verbose_name="商品")
    user_head_url = CharField(verbose_name="用户头像")
    user_name = CharField(verbose_name="用户名")
    good_info = CharField(max_length=500, verbose_name="购买商品的信息")   # 商品信息
    evaluate_time = DateTimeField(verbose_name="评价时间")
    content = TextField(default="", verbose_name="评论内容")
    star = IntegerField(default=0, verbose_name="评分")
    comment_nums = IntegerField(default=0, verbose_name="评论数")
    praised_nums = IntegerField(default=0, verbose_name="点赞数")
    image_list = TextField(default="", verbose_name="图片")
    video_list = TextField(default="", verbose_name="视频")


# 商品的评估总结信息字段
class GoodEvaluateSummary(BaseModel):
    # 这个Good是说属于哪个商品的评论，这是一个外键
    good = ForeignKeyField(Good, verbose_name="商品")
    tag = CharField(max_length=20, verbose_name="标签")
    num = IntegerField(default=0, verbose_name="数量")


if __name__ == "__main__":
    # 生成表结构
    db.create_tables([Good, GoodEvaluate, GoodEvaluateSummary])
























