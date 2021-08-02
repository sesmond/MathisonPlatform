#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: vincent
@file:testpid.py
@time:2021/07/08
"""
from subprocess import Popen

if __name__ == '__main__':
    command = "./app/test/test_cmd.sh"
    command = "python app/test/tset_sub.py"
    # p = Popen([command])
    p = Popen(['python', 'app/test/tset_sub.py'])
    # 'python', 'app/test/tset_sub.py']) 用这种方式返回的是相应的进程id。
    print(p.pid)
    # 用Popen执行，如果主进程结束了，子进程一定也结束。
    # 用shell再执行python，跑的是两个进程
    print()
    # xxx = os.system(command)
    # print(xxx)
