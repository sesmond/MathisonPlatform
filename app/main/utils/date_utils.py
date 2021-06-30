#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 日期工具类
@File    :   date_utils.py    
@Author  : vincent
@Time    : 2020/12/1 下午6:09
@Version : 1.0 
'''

import datetime
import time

from dateutil.relativedelta import relativedelta

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"


# 当前毫秒数
def curMilis():
    return int(time.time() * 1000)


# 当前秒数
def curSeconds():
    return int(time.time())


# 当前日期 格式%Y-%m-%d %H:%M:%S
def curDatetime():
    return datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT)


# 当前日期 格式%Y-%m-%d
def curDate():
    return datetime.date.today()


# 当前时间 格式%Y-%m-%d
def curTime():
    return time.strftime(TIME_FORMAT)


# 秒转日期
def secondsToDatetime(seconds):
    return time.strftime(DATETIME_FORMAT, time.localtime(seconds))


# 毫秒转日期
def milisToDatetime(milix):
    return time.strftime(DATETIME_FORMAT, time.localtime(milix // 1000))


# 日期转毫秒
def datetimeToMilis(datetimestr):
    strf = time.strptime(datetimestr, DATETIME_FORMAT)
    return int(time.mktime(strf)) * 1000


# 日期转秒
def datetimeToSeconds(datetimestr):
    strf = time.strptime(datetimestr, DATETIME_FORMAT)
    return int(time.mktime(strf))


# 当前年
def curYear():
    return datetime.datetime.now().year


# 当前月
def curMonth():
    return datetime.datetime.now().month


# 当前日
def curDay():
    return datetime.datetime.now().day


# 当前时
def curHour():
    return datetime.datetime.now().hour


# 当前分
def curMinute():
    return datetime.datetime.now().minute


# 当前秒
def curSecond():
    return datetime.datetime.now().second


# 星期几
def curWeek():
    return datetime.datetime.now().weekday()


# 几天前的时间
def nowDaysAgo(days):
    daysAgoTime = datetime.datetime.now() - datetime.timedelta(days=days)
    return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())


# 几天后的时间
def nowDaysAfter(days):
    daysAgoTime = datetime.datetime.now() + datetime.timedelta(days=days)
    return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())


# # 某个日期几天前的时间
# def dtimeDaysAgo(dtimestr, days):
#     daysAgoTime = datetime.datetime.strptime(dtimestr, DATETIME_FORMAT) - datetime.timedelta(days=days)
#     return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())


# 某个日期几天前的时间
def add_day(date_str, days):
    daysAgoTime = datetime.datetime.strptime(date_str, '%Y-%m-%d') + datetime.timedelta(days=days)
    return time.strftime('%Y-%m-%d', daysAgoTime.timetuple())


def add_year(date_str, years):
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    res = (d + relativedelta(years=years)).strftime('%Y-%m-%d')
    return res


def date_distance(start, end):
    """
    计算两个日期差多少天
    @param start:
    @param end:
    @return:
    """
    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    dis_days = end_date - start_date
    return dis_days.days


def check_format(date_str):
    '''
    校验日期字符串格式
    @param date_str:
    @return:
    '''
    date_arr = date_str.split('-')
    check_day = False
    if len(date_arr) == 2:
        year, month = date_arr
    elif len(date_arr) == 3:
        year, month, day = date_arr
        check_day = True
    else:
        return False
    if not str(year).isdigit():
        return False
    if len(year) != 4:
        return False
    else:
        if year[0] != '2':
            # 年不能以0开头
            return False
    if not str(month).isdigit():
        return False
    if int(month) > 12 or int(month) < 1:
        return False
    if check_day:
        # TODO !!
        if len(day) != 2:
            return False
        if not str(day).isdigit():
            return False
        if int(day) > 31 or int(day) < 1:
            return False
    return True


def get_num_from_to(s, start, end):
    """
    找出字符串从start 到end中的字符串, 遇到非数字停下来？
    @param s:
    @param start:
    @param end:
    @return:
    """
    rtn = ''
    if end > len(s):
        end = len(s)
    for i in range(start, end):
        if s[i].isdigit():
            rtn += s[i]
        else:
            continue
            # break
    return rtn


def isValidDate(date_str):
    try:
        # TODO!!
        datetime.date.fromisoformat(date_str)
    except:
        return False
    else:
        return True


if __name__ == '__main__':
    a = '2018-02-28'
    b = add_year(a, 1)
    c = add_day(b, -1)
    print(b)
    print(c)
    d = date_distance(a, b)
    print(d)
