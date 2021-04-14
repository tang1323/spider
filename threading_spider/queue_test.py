
from queue import Queue
import queue


if __name__ == "__main__":
    """
    以下是我们最常用的方法，也足够用了
    """
    # maxsize是最大长度
    message_queue = Queue(maxsize=2)

    # 用put消息队列里放数据
    message_queue.put("tangming")
    message_queue.put("tangming2")

    # 用get消息队列里取数据
    message = message_queue.get()
    print(message)

    message = message_queue.get()
    print(message)













    # print("start put tangming3")
    # # 如果超过最大长度，用put会一直阻塞着,timeout是说如果阻塞住，3秒后就会抛出一个异常
    # try:
    #     # 我们一般用这个put比较多
    #     # message_queue.put("tangming3", timeout=3)
    #
    #     # 还有一种方法，我们如果不想等程序直接用以下的
    #     message_queue.put_nowait("tangming3")
    #
    # # 我们可能经常使用Exception的话，是不好的，要尽量知道我们会抛出什么异常
    # except queue.Full as e:
    #     pass
    # print("end")












