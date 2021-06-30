#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : VO 转换工具类
@File    :   vo_utils.py    
@Author  : vin
@Time    : 2020/6/1 3:35 下午
@Version : 1.0 
'''
import numpy as np

from app.main.app.vo.response.base_response import PositionEntity, WordEntity


def boxes2vo(boxes):
    """
    ndarray 类型的 转换成vo类型
    :param boxes:
    :return:
    """
    result_box = []
    for box in boxes:
        result_box.append(box2pos(box))
    return result_box


def box2pos(box):
    """
    box 转换成PositionEntity 类型的list
    :param box:
    :return:
    """
    # print(type(box),box)
    box = np.array(box)
    # temp_box = box
    temp_box = np.reshape(box, (-1, 2))
    # print(type(temp_box),temp_box)
    box_pos = []
    for pts in temp_box:
        box_pos.append(PositionEntity(int(pts[0]), int(pts[1])))
    return box_pos


def convert_word_entity(boxes, text_arr, prob_arr=None):
    """
        构造word entity报文
    @param boxes: 文本框坐标（n,2）
    @param text_arr: 文本列表
    @param prob_arr: 文本置信度
    @return:
    """
    text = ""
    wordsInfo = []

    # 处理未分行的内容
    for i, box in enumerate(boxes):
        # logger.debug('文字:%s',text_arr[i])
        pos = []
        box = np.array(box)
        box = box.reshape(-1, 2)
        for pts in box:
            # logger.info("pts:%r",pts)
            pos.append(PositionEntity(int(pts[0]), int(pts[1])))
        word = WordEntity(text_arr[i], pos)
        if prob_arr:
            probs = prob_arr[i]
            prob = [float(_p) for _p in probs]
            word.prob = prob
        wordsInfo.append(word)
        text += text_arr[i] + " "
    return wordsInfo, text


def ndarray2list(boxes):
    if isinstance(boxes, list):
        boxes = np.array(boxes)
        return boxes.tolist()
    else:
        return boxes.tolist()


if __name__ == '__main__':
    from app.main.app.vo.response.detect_response_vo import DetectResponse
    from app.main.app.utils import json_utils

    response = DetectResponse()
    response.image = "qw"
    # 这个要求格式必须统一才能强转
    boxes_pred = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    boxes_pred_new = np.array(boxes_pred)
    response.boxes = boxes2vo(boxes_pred_new)
    response.sid = "sid"
    # response.boxes = boxes_pred
    result = json_utils.obj2json(response)
    print("after:", result)
