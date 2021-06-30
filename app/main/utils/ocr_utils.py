import logging
from json.decoder import JSONDecodeError

import base64
import cv2
import datetime
import json
import numpy as np
import requests

from app.main.app.utils import image_utils

logger = logging.getLogger("OCR Utils")


# 输入是[[x1,y1,x2,y2,x3,y3,x4,y4],]
#         |    |  ^     ^
def crop_small_images(img, polygens):
    logger.debug("图像：%r", img.shape)
    cropped_images = []
    for pts in polygens:
        # crop_img = img[y:y+h, x:x+w]
        # crop_img = img[int(pts[3]):int(pts[5]), int(pts[0]):int(pts[2])]
        # logger.debug("子图坐标：%r", pts)
        pts_new = np.array(pts).astype(np.int32)
        if len(pts_new.shape) == 1:
            pts_new = pts_new.reshape(-1, 2)
        crop_img = image_utils.four_point_transform(img, pts_new)
        # logger.debug("子图坐标：%r,%r", pts_new,crop_img.shape)
        cropped_images.append(crop_img)
    return cropped_images


# 处理将请求中的base64转成byte数组，注意，不是numpy数组
def base64_2_bytes(base64_data):
    logger.debug("Got image ,size:%d", len(base64_data))
    # 去掉可能传过来的“data:image/jpeg;base64,”HTML tag头部信息

    index = base64_data.find(",")
    if index != -1: base64_data = base64_data[index + 1:]
    # print(base64_data)
    # 降base64转化成byte数组
    buffer = base64.b64decode(base64_data)
    logger.debug("Convert image to bytes by base64, lenght:%d", len(buffer))

    return buffer


# 把json字符串转成dict字典，如果
def json2dict(request):
    str_data = request.get_data()
    # logger.debug("Got Web data:%d bytes", len(str_data))
    data = str_data.decode('utf-8')
    try:
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        data = json.loads(data)
    except JSONDecodeError as e:
        logger.error(data)
        logger.error("JSon数据格式错误")
        raise Exception("JSon数据格式错误:" + str(e))
    return data


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
    logger.debug("从web读取数据，长度:%r", len(buffer))

    if len(buffer) == 0:
        logger.error("图像解析失败，原因：长度为0")
        return None

    # 先给他转成ndarray(numpy的)
    data_array = np.frombuffer(buffer, dtype=np.uint8)

    # 从ndarray中读取图片，有raw数据变成一个图片GBR数据,出来的数据，其实就是有维度了，就是原图的尺寸，如160x70
    image = cv2.imdecode(data_array, cv2.IMREAD_COLOR)

    if image is None:
        logger.error("图像解析失败")  # 有可能从字节数组解析成图片失败
        return None

    logger.debug("从字节数组变成图像的shape:%r", image.shape)

    return image


def binary_image(img, threshold):
    """
    图片动态二值化
    :param img:
    :param threshold:
        如果值>0，就需要先进行二值化
        如果值为-1，则进行自适应二值化处理
        如果这个值为None/0，那么不进行二值化处理
    :return: 返回二值化后的图片（可能没有二值化）
    """
    if not threshold:
        return img
    threshold = int(threshold)
    if threshold == -1:
        logger.debug("对图片自适应二值化处理:%r", threshold)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
        # binary = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 5)
        new_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        return new_img
    elif threshold > 0:
        logger.debug("对图片阈值二值化处理,阈值:%r,图片：%r", threshold, img.shape)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # +cv2.THRESH_OTSU
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        new_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        return new_img
    else:
        logger.debug("二值化阈值为：%r,不能解析，原样返回", threshold)
        return img


# call CTPN得到坐标
# url=CFG['local']['url'] + "ocr"
def call_ocr(image, ctpn_url):
    base64_images = nparray2base64(image)
    post_data = {
        "img": base64_images,
        "sid": datetime.datetime.now().strftime("%Y%m%d%H%S%f")[:-3],
        "prob": False,
        "charInfo": False,
        "rotate": False,
        "table": False
    }
    response = requests.post(ctpn_url, json=post_data, headers={'Content-Type': 'application/json'})
    r = response.text
    # print(r)
    return parse_ctpn_json(json.loads(r))


# call CRNN识别服务，
# 参数：
# [
#     {"img": "$image1"},
#     {"img": "$image2"},
#     {"img": "$image3"},
#     {"img": "$image4"}
# ]
# 返回：
# {
#     "sid":"6c8f999fe943bd5ad325483fb860a3f0645e9b214bdffb4b6a4d9ae96ea9debb6b861c69",
#     "prism_wordsInfo":[
#         {"word":"供审核使用"},
#         {"word":"核实图片"}
#     ]
# }
def call_crnn(images, crnn_url):
    post_data = []
    for _img in images:
        base64_images = nparray2base64(_img)
        post_data.append({"img": base64_images})

    response = requests.post(crnn_url, json=post_data, headers={'Content-Type': 'application/json'})
    r = response.text
    # print(r)
    return parse_crnn_json(json.loads(r))


# 解析json结构
def parse_crnn_json(json_data):
    prism_wordsInfo = json_data['prism_wordsInfo']
    result = []
    for info in prism_wordsInfo:
        word = info['word']
        result.append(word)
    return result


# 解析json结构
def parse_ctpn_json(jsonLine):
    prism_wordsInfo = jsonLine['prism_wordsInfo']
    result = []
    for info in prism_wordsInfo:
        dataList = []
        word = info['word']
        for pos in info['pos']:
            x = pos['x']
            y = pos['y']
            dataList.append(x)
            dataList.append(y)
        dataList.append(word)
        dataStr = str(dataList).replace("[", "").replace("]", "").replace("\\", "")
        result.append(dataStr)
    return result


def chunks(list, n):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(list), n):
        yield list[i:i + n]


def chunks(list, n):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(list), n):
        yield list[i:i + n]


# 把返回的稀硫tensor，转化成对应的字符List
def sparse_tensor_to_str(indices, values, dense_shape, characters):
    values = np.array([characters[id] for id in values])

    number_lists = np.array([['\n'] * dense_shape[1]] * dense_shape[0], dtype=values.dtype)
    res = []

    for i, index in enumerate(indices):
        number_lists[index[0], index[1]] = values[i]

    for one_row in number_lists:
        res.append(''.join(c for c in one_row if c != '\n'))

    return res


# 把小框都画上，红色
def draw_poly(image, data, exclued_data=None, abnormal_data=None):
    data = np.int32([data])
    for pos in data:
        cv2.polylines(image, pos, isClosed=True, color=(0, 0, 255), thickness=1)

    if exclued_data is not None:
        exclued_data = np.int32([exclued_data])
        for pos in exclued_data:
            cv2.polylines(image, pos, isClosed=True, color=(0, 255, 255), thickness=1)

    if abnormal_data is not None:
        abnormal_data = np.int32([abnormal_data])
        for pos in abnormal_data:
            cv2.polylines(image, pos, isClosed=True, color=(0, 0, 0), thickness=1)

    return image


# 画矩形框，填充，透明
def draw_rectange(image, data):
    data = np.int32(data)
    overlay = image.copy()
    odd_row = True  # 奇数行
    for rec in data:
        p1 = tuple(rec[0].tolist())
        p2 = tuple(rec[1].tolist())
        # print(rec)
        # print(p1)
        # print(p2)
        if odd_row:
            cv2.rectangle(overlay, p1, p2, (255, 0, 0), -1)
        else:
            cv2.rectangle(overlay, p1, p2, (0, 255, 0), -1)

        odd_row = bool(1 - odd_row)
    alpha = 0.4  # Transparency factor.
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


plate_chars = ["京", "沪", "津", "渝", "冀", "晋", "蒙", "辽", "吉", "黑",
               "苏", "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘", "粤",
               "桂", "琼", "川", "贵", "云", "藏", "陕", "甘", "青", "宁",
               "新", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
               "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L",
               "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X",
               "Y", "Z", "港", "学", "O", "使", "警", "澳", "挂"]


# 将汉字转成序号存储，不想用中文保存文件名
def plate_chi2chars(plate):
    if plate is None: return "0000000"
    first = plate[:1]
    left = plate[1:]
    if first in plate_chars:
        first = plate_chars.index(first)
    else:
        first = 99
    return str(first) + left


# bboxes : 4点坐标[x1,y1,x2,y2,x3,y3,x4,y4]
def draw_bboxes(image, bboxes, color=(255, 0, 0), thick=1):
    if type(bboxes) == list: bboxes = np.array(bboxes)
    assert bboxes.shape[-1] == 8
    bboxes = bboxes.reshape((-1, 4, 2))
    cv2.polylines(image, bboxes, isClosed=True, color=color, thickness=thick)


def ndarray2list(boxes):
    new_boxes = []
    for box in boxes:
        box = np.array(box).tolist()
        new_boxes.append(box)
    return new_boxes


if __name__ == '__main__':
    print("")
    # image = cv2.imread("test/test.png")
    # polygens = [
    #     [0, 0, 100, 0, 100, 100, 0, 100]
    # ]

    # for img in crop_small_images(image, polygens):
    #     print("子图：", img.shape)
    #     # cv2.imshow("cropped", img)
    #     # cv2.waitKey(0)
    #     tobase64(img)
