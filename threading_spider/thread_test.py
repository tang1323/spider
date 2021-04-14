
# 1.实例化Thread
# 2.继承Thread
import time
from threading import Thread


# 1.实例化Thread
# 有时候调用的函数并没有return返回值，所以调用函数的方法名就行了
# 如果调用了方法，那就会返回一个None，会出现错误
def sleep_task(sleep_time):
    print("sleep {} seconds start!".format(sleep_time))
    time.sleep(sleep_time)
    print("sleep {} seconds end!".format(sleep_time))


# if __name__ == "__main__":
#     start_time = time.time()
#
#     # 如果在sleep_task函数里只有一个参数的话，在args=(2,)里的参数一定要加一个逗号在后面
#     t1 = Thread(target=sleep_task, args=(2,))
#     t1.setDaemon(True)  # 也就是说t1设置为守护线程
#     t1.start()
#
#     t2 = Thread(target=sleep_task, args=(3,))
#     t2.setDaemon(True)  # 也就是说t2设置为守护线程
#     t2.start()
#
#     # t1.join()
#     # t2.join()
#
#     time.sleep(1)
#     end_time = time.time()
#     print("last_time:{}".format(end_time-start_time), end='\n')


    """
    1.当开启一个程序的时候，会默认启动一个主线程
    在这里时间是一个主线程，从头跑到尾，虽然t1,t2还在跑，但是主线程不管两个子线程有没有跑完，主线程继续跑
    so在这里是有3个线程
    所以这里主线程带着这两个线程跑，继续往后执行时间，所以虽然这里在做了时间间隔
    但时间这个主线程并不等子线程就往后执行了
    几乎同时启动的
    """

    """
    2.如何在主线程等到其他线程执行以后才继续执行
    这里用  t1.join()
            t2.join()
    这样就先打印t1,t2这两个线程再执行计算时间
    
    假设一种情况。如果主线程让t1,t2在1秒钟内执行完任务，如果不执行完成
    就代表t1,t2出现问题了，
    那这两个线程就要跟着主线程退出关闭掉
    t2.setDaemon(True)  # 也就是说t2设置为守护线程
    在这里设置了时候段
    时间主线程结束了，因为子线程设有守护线程
    所以在这里主线程结束，子线程也跟着结束
    """


# 2.继承Thread
class SleepThread(Thread):
    # 这里如果只写__init__方法，它会提示让我们继承父类的方法
    # 继承父类方法也有好处，因为父类方法有很多初始化的工作
    # 我们要加上，这是一个好习惯
    def __init__(self, sleep_time):
        self.sleep_time = sleep_time
        super().__init__()

    # 若是用类来实现，那就得重载这个run方法，这是固定的
    def run(self):
        print("sleep {} seconds start!".format(self.sleep_time))
        time.sleep(self.sleep_time)
        print("sleep {} seconds end!".format(self.sleep_time))


if __name__ == "__init__":
    t1 = SleepThread(2)
    t2 = SleepThread(3)
    t1.start()
    t2.start()

















