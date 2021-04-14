
from peewee import *

db = MySQLDatabase('spider', host="127.0.0.1", port=3306, user="tangming", password='130796')


class Person(Model):
    name = CharField(max_length=20, null=True)
    birthday = DateField()

    class Meta:
        database = db    # This model uses the "people.db" database.

        # 指明一下数据库表名,如果没有名，那就用这个类的小写做为表名
        table_name = "users"


# 数据的增，删，改，查

if __name__ == "__main__":
    # db.create_tables([Person])

    # 生成数据， 这个就是像类操作一样，uncle_bob是类的实例
    from datetime import date
    # uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
    # uncle_bob.save()  # bob is now stored in the database
    #
    # uncle_bob = Person(name='tangming', birthday=date(1996, 7, 13))
    # uncle_bob.save()  # bob is now stored in the database

    # 查询数据(只获取一条) get方法在获取不到数据会抛出异常，要做try
    # 这是查找某一个列
    # tangming = Person.select().where(Person.name == 'tangming').get()
    # print(tangming.birthday)

    # 这是更精简的写法
    # tangming = Person.get(Person.name == 'Bob')
    # print(tangming.birthday)

    # 等同于这个mysql语句
    # "select * from person where name='Grandma L.'"

    # 获取全部数据
    # query是modelselect对象，也是列表，可以像列表那样操作，在后面加[1:]是取第二个数据
    # 这个取不到数据不会抛异常， 这是这个的好处，上面那个就会抛异常
    # query = Person.select().where(Person.name == 'Bob')
    # for person in query:
    #     print(person.name, person.birthday)


    # 修改
    # query = Person.select().where(Person.name == 'Bob')[1:]
    # for person in query:
    #     person.birthday = date(1972, 1, 17)
    #     person.save()   # 在没有数据的存在的时候新增数据， 存在的时候修改数据

    # 删除
    query = Person.select().where(Person.name == 'Bob')[1:]
    for person in query:
        person.delete_instance()



