# encoding:utf-8
# !/usr/bin/python3

import json
import math
import os

import cv2
import numpy as np

'''
    此文件用于图片做旋转增强
'''


def show(img, title='无标题'):
    """
    本地测试时展示图片
    :param img:
    :param name:
    :return:
    """
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    font = FontProperties(fname='/Users/yanmeima/workspace/ocr/crnn/data/data_generator/fonts/simhei.ttf')
    plt.title(title, fontsize='large', fontweight='bold', FontProperties=font)
    plt.imshow(img)
    plt.show()


def check_and_mk_path(path):
    """
    检测路径不存在则新建
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.mkdir(path)


def get_rotate_box(boxes, center, angle, new_center):
    '''
    旋转之后计算框
    :param boxes:
    :param center:
    :param theta:
    :return:
    '''
    theta = math.radians(-angle)
    cos_theta, sin_theta = math.cos(theta), math.sin(theta)

    print("旋转中心", center, '旋转角度：', angle, "新中心：", new_center)
    new_boxes = []
    for box in boxes:
        new_box = []
        # print("旋转前：", box)
        for pts in box:
            # print("点旋转前：",pts)
            # 在新中心位置的基础上发生偏移
            pts_new = [
                int((pts[0] - center[0]) * cos_theta - (pts[1] - center[1]) * sin_theta + new_center[0]),
                int((pts[0] - center[0]) * sin_theta + (pts[1] - center[1]) * cos_theta + new_center[1])
            ]
            # print('点旋转后：',pts_new)
            new_box.append(pts_new)
        # print("旋转后：", new_box)

        new_boxes.append(new_box)
    return new_boxes


def img_label_rotate(img, label_path, theta, angle):
    '''
    图像旋转和对应坐标旋转
    :param img:
    :param label_path:
    :param theta:
    :param angle:
    :return:
    '''
    h, w, _ = img.shape
    img_rotate = cv2.rotate(img, theta)
    h1, w1, _ = img_rotate.shape
    center = (int(w / 2), int(h / 2))
    new_center = (int(w1 / 2), int(h1 / 2))

    with open(label_path, "r") as f:
        json_data = json.load(f)
        new_shapes = []
        for category in json_data['shapes']:
            points = category['points']

            # 画线
            # points_arr = np.array(points,np.int32)
            # points_reshape = points_arr.reshape(-1, 1, 2)
            # cv2.polylines(img, [points_reshape], True, (0, 0, 255), 10)
            # show(img)

            newrect = get_rotate_box([np.array(points).astype(int)], center, -angle, new_center)[0]
            print("newrect:", newrect)
            # 画线
            # points_arr = np.array(newrect)
            # points_reshape = points_arr.reshape(-1, 1, 2)
            # cv2.polylines(img_rotate, [points_reshape], True, (0, 0, 255), 5)
            # show(img_rotate)

            new_label = {
                "label": category['label'],
                "points": newrect,
                "shape_type": category['shape_type']
            }
            new_shapes.append(new_label)

        # new_json = {
        #     "version": json_data["version"],
        #     "flags": json_data["flags"],
        #     "shapes": new_shapes,
        #     "imagePath": json_data["imagePath"],
        #     "imageData": json_data["imageData"],
        #     "imageHeight": json_data["imageHeight"],
        #     "imageWidth": json_data["imageWidth"]
        # }
    return json_data, new_shapes, img_rotate


def get_json(json_data, new_shapes, imagepath_new):
    new_json = {
        "version": json_data["version"],
        "flags": json_data["flags"],
        "shapes": new_shapes,
        "imagePath": imagepath_new,
        "imageData": json_data["imageData"],
        "imageHeight": json_data["imageHeight"],
        "imageWidth": json_data["imageWidth"]
    }
    return new_json


def main(images_label_dir):
    files = os.listdir(images_label_dir)
    for file in files:
        filename, ext = os.path.splitext(file)
        if ext != ".jpg" and ext != ".JPG":
            continue
        else:
            img_path = os.path.join(images_label_dir, file)
            print(img_path)
            label_path = os.path.join(images_label_dir + filename + ".json")
            img = cv2.imread(img_path)
            print(img.shape)

            # 旋转增强
            json_data, new_shapes, img_rotate_1 = img_label_rotate(img, label_path, theta=cv2.ROTATE_90_CLOCKWISE,
                                                                   angle=90)
            new_image_name = filename + "_1" + ext
            new_json = get_json(json_data, new_shapes, new_image_name)
            new_image_path = os.path.join(images_label_dir + new_image_name)
            new_json_path = os.path.join(images_label_dir + filename + "_1" + ".json")
            save_file(new_json, img_rotate_1, new_image_path, new_json_path)

            json_data, new_shapes, img_rotate_2 = img_label_rotate(img, label_path, theta=cv2.ROTATE_180, angle=180)
            new_image_name = filename + "_2" + ext
            new_json = get_json(json_data, new_shapes, new_image_name)
            new_image_path = os.path.join(images_label_dir + new_image_name)
            new_json_path = os.path.join(images_label_dir + filename + "_2" + ".json")
            save_file(new_json, img_rotate_2, new_image_path, new_json_path)

            json_data, new_shapes, img_rotate_3 = img_label_rotate(img, label_path,
                                                                   theta=cv2.ROTATE_90_COUNTERCLOCKWISE, angle=270)
            new_image_name = filename + "_3" + ext
            new_json = get_json(json_data, new_shapes, new_image_name)
            new_image_path = os.path.join(images_label_dir + new_image_name)
            new_json_path = os.path.join(images_label_dir + filename + "_3" + ".json")
            save_file(new_json, img_rotate_3, new_image_path, new_json_path)


def save_file(new_json, img_rotate, new_image_path, new_json_path):
    '''
    保存图像和文件
    '''
    cv2.imwrite(new_image_path, img_rotate)
    with open(new_json_path, "w", encoding='utf-8') as g:
        json.dump(new_json, g, indent=2, sort_keys=True, ensure_ascii=False)


# ceshi
# images_label_dir = "data/test/rotate/"

images_label_dir = "data/djz/labelme_split/"

if __name__ == "__main__":
    main(images_label_dir)
