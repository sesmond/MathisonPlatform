#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   :TODO
@File    :   calculate_utils.py    
@Author  : vincent
@Time    : 2020/10/30 11:32 上午
@Version : 1.0 
'''


def correct_rate(correct_cnt, fail_cnt):
    if correct_cnt is not None and fail_cnt is not None:
        all_cnt = correct_cnt + fail_cnt
        if all_cnt > 0:
            rate = correct_cnt / all_cnt
            rate = round(rate, 4) * 100
        else:
            rate = 0
    else:
        rate = 0
    return rate
