#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 表格工具类
@File    :   excel_utils.py
@Author  :  vincent
@Time    : 2021/1/7 下午4:08
@Version : 1.0
'''
import logging

import xlrd

logger = logging.getLogger(__name__)


def read_excel(file_path, name_json):
    """
    读取固定模板格式的excel
    #1. 第一个sheet页一定是主数据
    #2. 有列表嵌套数据时，根据字段类型判断，并找其他sheet页
    @param file_path: 读取文件
    @param name_json: 字段名配置
    @return:
    """
    # logger.info("读取excel：%r,sheet:%r", file_path, sheet_name)
    data = xlrd.open_workbook(file_path)
    table = data.sheet_by_index(0)
    # table = data.sheet_by_name(sheet_name)
    rows = table.nrows
    result = {}
    # logger.info("name_json:%r", name_json)
    for i in range(1, rows):
        # TODO 要跟着字段类型来，要不然没法读更多sheet页
        row = table.row_values(i)
        filed_name = row[0]
        field_config = name_json.get(filed_name)
        if not field_config:
            logger.error("excel中字段：%r,配置未找到。", filed_name)
            # break
            continue
        field_type = field_config['type']
        if field_type == 'str':
            filed_value = row[2]
        elif field_type == 'list':
            filed_value = []
            for j in range(2, len(row)):
                filed_value.append(row[j])
        elif field_type == 'array':
            # TODO
            small_table = data.sheet_by_name(row[1])
            small_cols = small_table.ncols
            small_rows = small_table.nrows
            small_title = small_table.col_values(0)
            filed_value = []
            for j in range(2, small_cols):
                small_value = {}
                col = small_table.col_values(j)
                for k in range(1, small_rows):
                    small_value[small_title[k]] = col[k]
                filed_value.append(small_value)
        else:
            raise Exception("字段类型不正确")
        result[filed_name] = filed_value
    return result
