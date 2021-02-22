import threading
from time import sleep
from string import ascii_lowercase


class MyThread1(threading.Thread):
    def __del__(self):
        pass

    def run(self):
        for i in range(len(ascii_lowercase)):
            print(i)
            sleep(1)


x = MyThread1()

x.start()
