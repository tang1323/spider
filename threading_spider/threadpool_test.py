
# 线程池的简单例子
"""
什么是线程池
在用消息队列做多线程的时候，每一个线程的工作量都不一样
比如在ParseTopicListThread里很快，但是很容易阻塞住了
那我们能不能维护指定数量的线程， 让这个线程去获取同一个消息队列， 取到什么url就解析url
这就是我们线程池的一个概念， 让这些线程通过一个queue去从队列里面取数据， 去执行想要的逻辑
"""
# 1.twitter Timeline
# timeline就好比发的一条微博信息
"""
timeline很明显看出是有一对多的关系，
一般这种情况我们会单独设计一张表来存一对多的关系 
这里有4张表
"""
# timeline = {
#     "author": "tangming",
#     "tags": ["teacher", "python"],
#     "images": ["a.com", "b.com"],
#     "timeline": {},
#     "create_time": "",
#
# }


"""timeline
tags
images
retweet
以上每一张表都要有一个线程来做插入
假设表有十几个，也是同样 的道理

"""

# 每个timeline的插入分成了多个线程的插入，就是timeline看看子线程有没有插入成功
# 多条timeline插入的话就意味着每个timeline都要管理自己的子线程

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed, FIRST_COMPLETED
import time


def sleep_task(sleep_time):
    print("sleep {}s".format(sleep_time))
    time.sleep(sleep_time)
    print("end")
    return "tangming"


# max_workers意思是可以实例化几个线程，如果有3 个任务的话，它会依次从这里取数据
# ThreadPoolExecutor内部也是维护了一个队列， 你任务再多，就往队列里放，线程池会依次去做
executor = ThreadPoolExecutor(max_workers=2)

# 现在是将我们的任务发放, 这里的2是要这样写的(具体看submit这个函数)，不像在某个函数是要传一个元组（2，）
task1 = executor.submit(sleep_task, 2)
task2 = executor.submit(sleep_task, 3)
task3 = executor.submit(sleep_task, 3)


"""
因为这里有两个线程，在ThreadPoolExecutor里有个队列，所以这里只能做2个任务，
在第三个是在排队的，在等待前两个完成
所以在这里能用cancel()取消掉
这就是它内部的一个大概调度过程

"""
# print(task1.cancel())
# print(task2.cancel())
# print(task3.cancel())




# 这是取消程序的，但是！！！！运行中的程序是无法取消的
# 那这个有什么用cancel()
# cancel_status = task1.cancel()
# print(cancel_status)




# 等2秒
# time.sleep(2)
# # 可以用这个看看这个线程是否完成
# print(task1.done())


"""
使用wait()等待所有线程执行完成再执行你想要的代码逻辑
[]里面的参数是等待哪一些线程完成再执行其他代码
return_when的意思是什么时候才wait成功了，这里用这个ALL_COMPLETED是等待全部完成
"""
# wait([task1, task2, task3], return_when=ALL_COMPLETED)
# print("main end")


"""
这里我们想知道线程池里哪些线程是己经完成的，我们要立马知道这个线程，我们用as_completed
用as_completed，哪些线程完成了，它会立马通知我们
"""
# 这个可以进行遍历，这样哪个线程完成我们就能马上知道
all_task = [task1, task2, task3]
for task in as_completed(all_task):
    # task.result()是可以获取函数里的返回值的
    print(task.result())












