from threading import Thread
from threading import Lock  # 引入锁这个概念来做线程的同步
# gil是cpython的产物，就是python的解释器，就好比jam对java ，但是python还有其他解释器比如：jython, pypy
# 1.既然gil保证安全， 但是gil又有时间片的概念
# 2.gil会保证字节码的安全


"""
线程间的同步非常的重要
线程同步是什么意思：在我这个代码运行的时候不会被打断
也就是说先执行我这个代码完成后再执行其他的代码

一般我们都会用锁的概念来解决这类问题，很多编程语言都有锁这个概念
也就是在某段代码加一个锁，加了这个锁这段代码 就不会被打断

举例：在实际中，比如两个人在向库存购物，假设有100，但是两个人同时购买，当第一个人购买时
但还没有向数据库-1操作，即将要更新数据库减1操作，这时另一个人也正在购买，也正要执行更新数据库-1操作，但是两个人同时减1
但明明是买了2个商品出去，应该是98，但是由于多线程不知道什么到哪个线程（这也是最大的难点）
所以这时我们可以做线程同步，既加一个锁，必须我这个线程里的锁完成结束了
下个线程才能开始，
这就是线程同步
"""

total = 0

# 声明一个锁
total_lock = Lock()


def add():
    # 拿到 这个锁
    total_lock.acquire()
    global total
    for i in range(1000000):
        total += 1
    # 这里要释放这个锁，如果不写这段话，那其他线程就会一直等待
    total_lock.release()


def desc():

    # 在这里要保证是两个线程都用的是global total这个值，所以我们这里是用共同的锁
    # 拿到 这个锁
    total_lock.acquire()
    global total
    for i in range(1000000):
        total -= 1
    # 这里要释放这个锁，如果不写这段话，那其他线程就会一直等待
    total_lock.release()


if __name__ == "__main__":
    add_thread = Thread(target=add)
    desc_thread = Thread(target=desc)

    add_thread.start()
    desc_thread.start()

    # 等线程运行完之后才print()
    add_thread.join()
    desc_thread.join()

    print(total)















