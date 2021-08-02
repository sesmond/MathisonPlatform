#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: vincent
@file:tset_sub.py
@time:2021/07/08
"""
import os
import time


def test_ain():
    t = 0
    while True:
        print("循环中：", os.getpid(), "hellow", t)
        t += 1
        time.sleep(1)
        if t > 100:
            break


if __name__ == '__main__':
    test_ain()
