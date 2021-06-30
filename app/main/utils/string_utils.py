#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 字符串工具类
@File    :   string_utils.py
@Author  : vincent
@Time    : 2020/9/15 11:14 上午
@Version : 1.0
'''
import os


def is_null(obj):
    if obj is None:
        return True
    if len(obj) == 0:
        return True


def list_2_str(str_list):
    r_str = ''
    if str_list:
        for s in str_list:
            r_str = r_str + str(s) + "\n"
    return r_str


def to_str(obj):
    if not obj:
        return ""
    str1 = replace((str(obj)))
    return str1


def replace(str1):
    str1 = str1.replace("(", "（")
    str1 = str1.replace(")", "）")
    return str1


def equals(str1, str2):
    str1 = replace(to_str(str1))
    str2 = replace(to_str(str2))
    if str1 == str2:
        return True
    else:
        return False


def equals_list(list1, list2):
    str1 = list_2_str(list1)
    str2 = list_2_str(list2)
    return equals(str1, str2)


def create_header_line(file_name, max_len=70):
    s_len = len(file_name)
    if s_len >= max_len:
        return file_name
    w_size = (max_len - s_len) // 2
    t_str = "-" * w_size
    return t_str + file_name + t_str


def create_header_link(channel, data_type, file_name):
    file_name = os.path.split(file_name)[-1]  # file_name is full path with dirs, we only need the last file name

    file_name_a = '<a  href="./case_ocr.html?data_type=' + data_type + '&file_name=' + file_name \
                  + "&channel=" + channel \
                  + '"  target="_blank">' + file_name + '</a>'
    return file_name_a


def create_demo_link(case_type, ip_address, file_name):
    img_name = os.path.basename(file_name)
    file_name_a = '<a  href="./demo_result.html?case_type=' + case_type + '&ip_address=' + ip_address \
                  + "&file_name=" + img_name \
                  + '"  target="_blank">' + img_name + '</a>'
    return file_name_a


def rate_format(rate):
    """
    传入rate的小数格式，返回百分比格式的字符串
    @param rate:
    @return:
    """
    filed_rate = rate * 100
    rate_str = "{:.2f}".format(filed_rate)
    return rate_str


def temp_reg_date_format(date_str):
    if date_str and len(date_str) >= 7:
        return date_str[0:7]
    else:
        return date_str


def temp_duration_format(duration: str):
    if duration:
        d_arr = duration.split("至")
        if len(d_arr) == 2:
            return temp_reg_date_format(d_arr[0]) + "至" + temp_reg_date_format(d_arr[1])
        else:
            return duration
    else:
        return duration


def create_compare_result(gt_value, pred_value):
    if gt_value == pred_value:
        result_str = "<p>{}<p>".format("正确")
    else:
        result_str = "<p style=\"color:red\">{}<p>".format("错误")
    return result_str
