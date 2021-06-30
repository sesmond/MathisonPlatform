#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import cv2
import numpy as np

from app.main.app.utils import ocr_utils

logger = logging.getLogger(__name__)


# 把一个过高的行分割成多行
def split_high_row(rows, row_elements, row_avarage_height):
    logger.debug("一共%d行，行均高mean+1std:%f" % (len(rows), row_avarage_height))

    # 确定行高，通过小框门的均值+2sigma

    # 看返回的行的行高和这个均高的误差，如果超过2倍，就认为是2行重叠了，就要分拆
    # 分拆的算法：
    #   先要规定什么叫1行，我们认为是1.5倍的（均值+2sigma）是一个合理的行高
    #   确定了行高就好办了，就挨个把每个框归队即可
    #   行的起始Y是框们的左上角排序后，第一个框的左上角Y值
    #   只要这个框的左上角在范围内，就收纳之，归队！

    new_rows_elements = []
    new_rows = []

    for i in range(rows.shape[0]):
        row = rows[i]

        # 得到这行的行高
        row_height = abs(row[1] - row[0])

        # 如果这行在标准差的2倍以内，就认为是正常行，不处理
        # TODO:行高小于标准差的一半的舍弃
        if row_height < 2 * row_avarage_height:
            if row_height > row_avarage_height / 2:
                sorted_row_elements = split_line(row_elements, i)
                new_rows.append(row)
                new_rows_elements.append(sorted_row_elements)
                # new_rows_elements.append(row_elements[i])
            # logger.debug("此行高%f在2倍均高内，属于正常行" % row_height)
            continue

        logger.debug("此行高%f超过2倍均高%f，需要分拆...", row_height, 2 * row_avarage_height)

        # 找到对应行的所有的框，里面是9个长度，最后一个是字符
        polys = row_elements[i]
        # logger.debug("对行内小框们排序前结果：%s", polys)

        # TODO:每行按坐上顶点的x坐标从小到大排序
        # 按左上角排序,从小到大，返回的是一个list，不是numpy？
        sorted_polys = sorted(polys, key=lambda k: float(k[0]))  # 按照第一个点的纵坐标排序
        # logger.debug("对行内小框们按照左上角坐标排序后结果：%s",sorted_polys)

        new_row_height = row_avarage_height * 1.5  # <------------------------------------------------ 这个是最关键的，确定行高
        logger.debug("新行高为均高的1.5倍")

        left_polys_of_row = sorted_polys
        while (len(left_polys_of_row) != 0):

            # 得到新行的起始位置，就是最靠上poly的左上角坐标
            new_row_y1 = float(left_polys_of_row[1][1])
            new_row_y2 = new_row_y1 + new_row_height
            logger.debug("确定新行的y1:%d,y2:%d" % (new_row_y1, new_row_y2))

            # 然后用新的y1,y2去过滤小框们，形成一个新行，直到处理完毕
            left_polys_of_row = []
            new_poloys_of_row = []
            exclude_poloys_of_row = []

            for poly in left_polys_of_row:
                p_y2 = float(poly[5])  # x1,y1,x2,y2,x3,y3
                # 如果点的左下角的y值，小于新行的下沿，就并入此行
                if p_y2 <= new_row_y2:
                    logger.debug("此框在新行的内，加入新行集合")
                    new_poloys_of_row.append(poly)
                else:
                    exclude_poloys_of_row.append(poly)

            new_row = [new_row_y1, new_row_y2]
            new_rows.append(new_row)
            new_rows_elements.append(new_poloys_of_row)
            logger.debug("%d个小框加入新行%r" % (len(new_poloys_of_row), new_row))

            # 剔除已经归队的小框门，继续这个过程，直到为空
            left_polys_of_row = exclude_poloys_of_row
            logger.debug("排序的原有行的小框数量剩余：%d,剔除: %d" % (len(left_polys_of_row), len(new_poloys_of_row)))

    return new_rows, new_rows_elements


def split_line(row_elements, i):
    polys = row_elements[i]
    # logger.debug("对行内小框们排序前结果：%s", polys)

    # TODO:每行按坐上顶点的x坐标从小到大排序
    # 按左上角排序,从小到大，返回的是一个list，不是numpy？
    sorted_polys = sorted(polys, key=lambda k: float(k[0]))  # 按照第一个点的纵坐标排序
    # logger.debug("对行内小框们按照左上角坐标排序后结果：%s", sorted_polys)
    sorted_row_elements = sorted_polys

    return sorted_row_elements


# 剔除一个标准差之外的数据
# raw_data,原始数据[N,4,2] : [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
def exclude_1sigma(raw_data):
    # logger.debug(raw_data)

    # 把[N,4,2]变成[N],里面放着每个框的高度
    # for p in raw_data: logger.debug(p)

    data = np.array(raw_data)
    data = np.array(data[:, :8], np.float)
    # logger.debug(data)
    data = data.reshape(-1, 4, 2)
    data = np.abs(data[:, 0, 1] - data[:, 3, 1])
    # logger.debug(data)
    # logger.debug("小框高度方差：%r",np.std(data))
    # logger.debug(data.shape)
    # 求方差
    std = data.std()
    max = data.max()
    min = data.min()
    mean = data.mean()
    logger.debug("数据情况：mean={},std={},max={},min={}".format(mean, std, max, min))

    # 确定最大行高标准 2*均值（TODO：均值未来是否考虑刨除1sigma的？）
    max_row_height = 2 * mean

    # good_data_indices = np.where( np.abs(data - mean) < 3*std ) # 2sigma，95%
    # bad_data_indices = np.where(np.abs(data - mean) >= 3 * std)  # 2sigma，95%
    good_data_indices = np.where(data <= max_row_height)
    bad_data_indices = np.where(data > max_row_height)
    good = [raw_data[i] for i in good_data_indices[0]]
    bad = [raw_data[i] for i in bad_data_indices[0]]

    logger.debug("一共有%d个框，使用%d个做判断" % (
        len(data),
        len(good_data_indices[0])))
    return good, max_row_height, bad


# 剔除怪异的框:空字符或者只有1个字符
def exclude_abormals_by_text(raw_data):
    abnormal_data = []
    left_data = []
    for d in raw_data:
        # print('d:',d[8])
        if d[8].strip() == '':
            abnormal_data.append(d)
            continue

        if len(d[8].strip()) == 1:
            abnormal_data.append(d)
            continue

        if len(d[8].strip()) == 2:
            abnormal_data.append(d)
            continue

        left_data.append(d)

    return left_data, abnormal_data


# 输入：是图片高度，和小框们
# 输出：每一个行的起始和终止Y值，如：[[0,15],[28,35],...]
# 这个方法，只是看投影，只要有投影，就说明还是在一个大的行内，所以，他的问题是，可能会切割出很高的行
# 高行会在后面处理
def recognize_row(data, image_height):
    h_array = np.zeros(image_height, dtype=np.int32)

    # 先都往y轴上做投影
    for poly in data:  # 一个框
        poly = poly[:8]  # 去除文本
        poly = np.array(poly, np.float).astype(np.int32)
        poly = poly.reshape(4, 2)

        y1 = poly[0, 1]
        y2 = poly[3, 1]
        # x_min = poly[0,0]

        # 向Y轴做投影
        h_array[y1:y2] = 1

    pre_value = 0
    rows = []

    # 从0跃迁到1的连续区间，记录其开始、结束为止，即投影线段，h_array是一个图像高为长度的一个0/1数组
    for i, value in enumerate(h_array.tolist()):
        if pre_value == 0 and value == 1:
            rows.append(i)
        if pre_value == 1 and value == 0:
            rows.append(i)
        pre_value = value

    # 让最后的点是偶数
    if len(rows) % 2 != 0: np.append(rows, image_height)

    rows = np.array(rows)
    rows = rows.reshape(-1, 2)

    # 每个框都归队
    row_elements = []
    for row in rows:
        one_row_elements = []

        remove_index = []
        # logger.debug("处理一行：%r",row)
        for d in data:  # 一个框

            poly = d[:8]
            poly = np.array(poly, np.float).astype(np.int32)
            poly = poly.reshape(4, 2)
            y1 = poly[0, 1]
            y2 = poly[3, 1]
            # x_min = poly[0, 0]

            # 如果这个框的投影在某个行内，就归队到这行，然后在总集合中剔除他
            if y1 >= row[0] and y2 <= row[1]:
                # print("y1,y2,row_y1,row_y2:", y1, y2, row[0], row[1])

                # TODO:每行按坐上定点的x坐标从小到大排序
                one_row_elements.append(d)
                # logger.debug("这个框的投影在行内，归队TA，并在总集合中剔除他:y1(%d)>row_y1(%d),y2(%d)<row_y2(%d)" % (y1,row[0],y2,row[1]))
        row_elements.append(one_row_elements)

    # rows和row_elements行数是一样的，对应行就是对应的框们
    return rows, row_elements


# ../ctpn/data/train/labels/2019040107140584812123234.txt
# data shape是[N,9],前8个是坐标，最后一个是文本
def process(image_shape, data):
    left_data, abnormal_data = exclude_abormals_by_text(data)
    logger.debug("踢出文本异常：%d=>%d" % (len(data), len(left_data)))

    left_data, avarage_row_heigt, exclued_data = exclude_1sigma(left_data)

    height, width, _ = image_shape
    rows, row_elements = recognize_row(left_data, height)
    rows, row_elements = split_high_row(rows, row_elements, avarage_row_heigt)
    logger.debug("最终切分出[%d]行rows和[%d]行row_elements", len(rows), len(row_elements))

    # rows_elements包含着正常的在行内的框
    # excluded_data包含着不包含在行内的框
    # abnromal_data包含着文本上异常的框：空串或者啥
    return rows, row_elements, exclued_data, abnormal_data


if __name__ == '__main__':

    # path = "../ctpn/data/train/labels/2019040107140584812123234.txt"
    path = "../data/vehicle/labels/27614.txt"
    f = open(path, "r", encoding='utf-8')
    lines = f.readlines()
    # logger.debug(lines)

    # from test import test_vehicle_recoginze
    # data = test_vehicle_recoginze.text_line_to_list(lines)

    data = []
    # 190.0,276.0,477.0,276.0,477.0,293.0,190.0,293.0
    for line in lines:
        cord = []
        cords = line.split(",")
        cord = [float(c) for c in cords[:8]]
        # cord = [int(c) for c in cords[:8]]
        # cord += cords[8:]
        data.append(cord)

    data = np.array(data)
    data.astype(int)

    image = cv2.imread("../data/vehicle/images/27614.jpg")

    rows, row_elements, exclued_data, abnormal_data = process(image.shape, data)

    _, width, _ = image.shape

    # 准备矩形框数据：[N,2] => [N,2，2]
    # [[y1,y2],...] => [[[10,y1],[790,y2]],...]
    rec_data = np.expand_dims(rows, axis=2)
    zeros = np.zeros(rec_data.shape)
    rec_data = np.concatenate((zeros, rec_data), axis=2)
    rec_data[:, 0, 0] = 10  # p1(10,y1)
    rec_data[:, 1, 0] = width - 10  # p1(width-10,y2)
    ocr_utils.draw_rectange(image, rec_data)

    # 把小框画上去
    ocr_utils.draw_poly(image, data, exclued_data, abnormal_data)
