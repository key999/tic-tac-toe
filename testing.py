import threading
from time import sleep
from string import ascii_lowercase


class MyThread1(threading.Thread):
    def run(self):
        for i in range(len(ascii_lowercase)):
            print(i)
            sleep(1)


class MyThread2(threading.Thread):
    def run(self):
        for i in ascii_lowercase:
            print(i)
            sleep(1)


x = MyThread1()
y = MyThread2()

x.start()
y.start()

x.join()
y.join()
