#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   :  图片工具类
@File    :   image_utils.py
@Author  :  vicent
@Time    : 2020-02-05 16:09
@Version : 1.0
'''
import base64
import math

import cv2
import numpy as np


def distance(p1, p2, p):
    return abs(((p2[1] - p1[1]) * p[0] - (p2[0] - p1[0]) * p[1] + p2[0] * p1[1] - p2[1] * p1[0]) /
               math.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2))


def antipodal_pairs(convex_polygon):
    """
    对跖
    :param convex_polygon:
    :return:
    """
    l = []
    n = len(convex_polygon)
    p1, p2 = convex_polygon[0], convex_polygon[1]

    t, d_max = None, 0
    for p in range(1, n):
        d = distance(p1, p2, convex_polygon[p])
        if d > d_max:
            t, d_max = p, d
    l.append(t)

    for p in range(1, n):
        p1, p2 = convex_polygon[p % n], convex_polygon[(p + 1) % n]
        _p, _pp = convex_polygon[t % n], convex_polygon[(t + 1) % n]
        while distance(p1, p2, _pp) > distance(p1, p2, _p):
            t = (t + 1) % n
            _p, _pp = convex_polygon[t % n], convex_polygon[(t + 1) % n]
        l.append(t)

    return l


# returns score, area, points from top-left, clockwise , favouring low area
def mep(convex_polygon):
    def compute_parallelogram(convex_polygon, l, z1, z2):
        def parallel_vector(a, b, c):
            v0 = [c[0] - a[0], c[1] - a[1]]
            v1 = [b[0] - c[0], b[1] - c[1]]
            return [c[0] - v0[0] - v1[0], c[1] - v0[1] - v1[1]]

        # finds intersection between lines, given 2 points on each line.
        # (x1, y1), (x2, y2) on 1st line, (x3, y3), (x4, y4) on 2nd line.
        def line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
            px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
                    (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
            py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
                    (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
            return px, py

        # from each antipodal point, draw a parallel vector,
        # so ap1->ap2 is parallel to p1->p2
        #    aq1->aq2 is parallel to q1->q2
        p1, p2 = convex_polygon[z1 % n], convex_polygon[(z1 + 1) % n]
        q1, q2 = convex_polygon[z2 % n], convex_polygon[(z2 + 1) % n]
        ap1, aq1 = convex_polygon[l[z1 % n]], convex_polygon[l[z2 % n]]
        ap2, aq2 = parallel_vector(p1, p2, ap1), parallel_vector(q1, q2, aq1)

        a = line_intersection(p1[0], p1[1], p2[0], p2[1], q1[0], q1[1], q2[0], q2[1])
        b = line_intersection(p1[0], p1[1], p2[0], p2[1], aq1[0], aq1[1], aq2[0], aq2[1])
        d = line_intersection(ap1[0], ap1[1], ap2[0], ap2[1], q1[0], q1[1], q2[0], q2[1])
        c = line_intersection(ap1[0], ap1[1], ap2[0], ap2[1], aq1[0], aq1[1], aq2[0], aq2[1])

        s = distance(a, b, c) * math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
        return s, a, b, c, d

    z1, z2 = 0, 0
    n = len(convex_polygon)
    # 每一条边 找他的对拓顶点
    # for each edge, find antipodal vertice for it (step 1 in paper).
    l = antipodal_pairs(convex_polygon)

    so, ao, bo, co, do, z1o, z2o = 100000000000, None, None, None, None, None, None

    # step 2 in paper.
    for z1 in range(0, n):
        if z1 >= z2:
            z2 = z1 + 1
        p1, p2 = convex_polygon[z1 % n], convex_polygon[(z1 + 1) % n]
        a, b, c = convex_polygon[z2 % n], convex_polygon[(z2 + 1) % n], convex_polygon[l[z2 % n]]
        if distance(p1, p2, a) >= distance(p1, p2, b):
            continue

        while distance(p1, p2, c) > distance(p1, p2, b):
            z2 += 1
            a, b, c = convex_polygon[z2 % n], convex_polygon[(z2 + 1) % n], convex_polygon[l[z2 % n]]

        st, at, bt, ct, dt = compute_parallelogram(convex_polygon, l, z1, z2)

        if st < so:
            so, ao, bo, co, do, z1o, z2o = st, at, bt, ct, dt, z1, z2

    return so, ao, bo, co, do, z1o, z2o


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


def four_point_transform(image, pts):
    """
        根据四点坐标切出图片,并透射变换为矩形输出
    :param image:
    :param pts: 4,2格式的
    :return:
    """
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

    # 获取仿射变换矩阵并应用它
    M = cv2.getPerspectiveTransform(rect, dst)
    # 进行仿射变换
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # 返回变换后的结果
    return warped


def crop_img_with_area(image, pts):
    warped = four_point_transform(image, pts)
    # 添加面积输出
    return warped, warped.shape[0] * warped.shape[1]


def rotate_angle(img, angle):
    """
    图片旋转某个角度
    @param img:
    @param angle:
    @return:
    """
    height, width = img.shape[:2]
    heightNew = int(
        width * math.fabs(math.sin(math.radians(angle))) + height * math.fabs(math.cos(math.radians(angle))))
    widthNew = int(height * math.fabs(math.sin(math.radians(angle))) + width * math.fabs(math.cos(math.radians(angle))))
    matrix = cv2.getRotationMatrix2D((int(img.shape[1] / 2), int(img.shape[0] / 2)), angle, 1)
    matrix[0, 2] += (widthNew - width) / 2
    matrix[1, 2] += (heightNew - height) / 2
    img_rotate = cv2.warpAffine(img, matrix, (widthNew, heightNew), borderValue=(255, 255, 255))
    return img_rotate


# 必须按照vgg的要求resize成224x224的，变形就变形了，无所了，另外还要normalize，就是减去那三个值
def prepare4vgg(image_list):
    result = []
    for image in image_list:
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        image = image[:, :, ::-1]  # BGR->RGB
        # result.append(mean_image_subtraction(image)) #减去均值
        result.append(image)  # 因为后面模型中减均值了，所以这里不作处理
    return np.array(result)


# [123.68, 116.78, 103.94] 这个是VGG的预处理要求的，必须减去这个均值：https://blog.csdn.net/smilejiasmile/article/details/80807050
def mean_image_subtraction(images, means=[124, 117, 104]):  # means=[123.68, 116.78, 103.94]):
    # 干啥呢？ 按通道，多分出一个维度么？
    for i in range(3):
        images[:, :, i] = images[:, :, i] - means[i]
    return images


def nparray2base64(data):
    if type(data) == list:
        result = []
        for d in data:
            _, buf = cv2.imencode('.jpg', d)
            result.append(str(base64.b64encode(buf), 'utf-8'))
        return result

    _, d = cv2.imencode('.jpg', data)
    return str(base64.b64encode(d), 'utf-8')


def base64_2_image(base64_data):
    data = base64_2_bytes(base64_data)
    return bytes2image(data)


# 从web的图片RGB的byte数组，转换成cv2的格式
def bytes2image(buffer):
    if len(buffer) == 0:
        print("图像解析失败，原因：长度为0")
        return None

    # 先给他转成ndarray(numpy的)
    data_array = np.frombuffer(buffer, dtype=np.uint8)

    # 从ndarray中读取图片，有raw数据变成一个图片GBR数据,出来的数据，其实就是有维度了，就是原图的尺寸，如160x70
    image = cv2.imdecode(data_array, cv2.IMREAD_COLOR)

    if image is None:
        return None

    return image


# 处理将请求中的base64转成byte数组，注意，不是numpy数组
def base64_2_bytes(base64_data):
    # 去掉可能传过来的“data:image/jpeg;base64,”HTML tag头部信息

    index = base64_data.find(",")
    if index != -1: base64_data = base64_data[index + 1:]
    # print(base64_data)
    # 降base64转化成byte数组
    buffer = base64.b64decode(base64_data)

    return buffer


def read_base64(img_path):
    # TODO base64图片的转化
    with open(img_path, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        s = base64_data.decode()
    return s


def read_base64_cv2(img_path):
    img = cv2.imread(img_path)
    img1 = nparray2base64(img)
    return img1


if __name__ == '__main__':
    def write_img(base64_str, img_name):
        imgdata = base64.b64decode(base64_str)
        file = open(img_name, 'wb')
        file.write(imgdata)
        file.close()


    # convex_polygon = [[86, 701], [272, 808], [289, 897], [97, 791]]
    # convex_polygon = np.array(convex_polygon)
    # area, v1, v2, v3, v4, _, _ = mep(convex_polygon)
    img_p = "data/txt/ori.jpg"
    img = cv2.imread(img_p)
    img1 = nparray2base64(img)
    img2 = read_base64(img_p)
    print(img2)
    print("")
    f = open("data/txt/1.txt", "w")
    f.write(img1)
    f1 = open("data/txt/2.txt", "w")
    f1.write(img2)
    write_img(img1, "data/txt/1.jpg")
    write_img(img2, "data/txt/2.jpg")
