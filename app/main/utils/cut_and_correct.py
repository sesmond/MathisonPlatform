# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os

import cv2
import numpy as np

'''
    根据任意四边形的四点坐标，切出外接矩形框或者做放射矫正，切出矩形
'''

logger = logging.getLogger(__name__)


def init_logger():
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.DEBUG,
        handlers=[logging.StreamHandler()])


def order_points(pts):
    # 初始化坐标点
    rect = np.zeros((4, 2), dtype="float32")

    # 获取左上角和右下角坐标点
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # 分别计算左上角和右下角的离散差值
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def crop_img(image, pts):
    # 获取坐标点，并将它们分离开来
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # 计算新图片的宽度值，选取水平差值的最大值
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # 计算新图片的高度值，选取垂直差值的最大值
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # 构建新图片的4个坐标点
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # 获取透视变换矩阵并应用它
    M = cv2.getPerspectiveTransform(rect, dst)
    # 进行透视变换
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # 返回变换后的结果
    return warped, warped.shape[0] * warped.shape[1]


def read_json(json_path):
    # 读取json文件内容,返回字典格式
    with open(json_path, 'r', encoding='utf8') as fp:
        json_data = json.load(fp)
        # logger.info('这是文件中的json数据:%s', json_data)
        logger.info('这是读取到文件数据的数据类型:%s', type(json_data))
        points = json_data['shapes'][0]['points']
        logger.info("返回四点坐标:%s", points)

        # cut_img(points) # 切图
    return points


def cut_img(points):
    # 切图
    img_path = "data/images/9.jpg"
    img = cv2.imread(img_path)
    x = []
    y = []
    for p in points:
        x.append(p[0])
        y.append(p[1])
    x_min = min(x)
    y_min = min(y)
    x_max = max(x)
    y_max = max(y)
    w = x_max - x_min
    h = y_max - y_min

    cut_img = img[y_min:y_min + h, x_min:x_min + w]
    cv2.imwrite("data/cut/9.jpg", cut_img)


def main(path, images_path):
    files = os.listdir(path)
    for file in files:
        logger.debug("处理文件:%s", file)
        name, _ = os.path.splitext(file)
        img_path = os.path.join(images_path + name + ".jpg")
        image = cv2.imread(img_path)

        if image is None:
            continue
        else:
            json_path = path + file
            points = read_json(json_path)
            points = np.array(points)
            warped = crop_img(image, points)

    return warped, name


path = "data/frame/"
images_path = "data/images/"
correct_path = "data/correct/"

if __name__ == "__main__":
    init_logger()
    warped, name = main(path, images_path, correct_path)

    image_path = os.path.join(correct_path + name + ".jpg")
    cv2.imwrite(image_path, warped[0])

# 测试
# if __name__ == "__main__":
# points, image = cut_img()
# print("points:",points)
# points = np.array(points)
# warped = crop_plate(image, points)
# print("warped:",warped)
# cv2.imwrite("data/correct/9.jpg",warped[0])
