# -*- coding:utf-8 -*-
import logging
import os

import config
import cv2
import requests
from own_ocr import nparray2base64

CFG = config.CFG

logger = logging.getLogger("身份证图片识别")


def init_logger():
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.DEBUG,
        handlers=[logging.StreamHandler()])


key_pos = {
    '姓': [[45, 60], [65, 75]],
    '名': [[80, 60], [95, 75]],
    '性': [[45, 107], [63, 123]],
    '别': [[78, 109], [96, 126]],
    '族': [[222, 109], [238, 126]],
    '出': [[46, 156], [62, 173]],
    '生': [[78, 158], [95, 174]],
    '年': [[189, 157], [204, 173]],
    '住': [[45, 210], [65, 225]],
    '址': [[79, 208], [96, 225]],
    '公': [[47, 335], [68, 360]],
    '民': [[70, 335], [87, 360]],
    '身': [[89, 335], [112, 360]],
    '份': [[111, 335], [135, 360]],
    '号': [[152, 335], [172, 360]],
    '码': [[170, 335], [200, 360]]
}


def crnn(images, url='default_url'):
    """
     多张图片的crnn
    :param images_base64:
    :param url:crnn的地址，可以动态传入，以测试不同版本的crnn
    :return:
    """
    if url == 'default_url':
        url = CFG['local']['url'] + "crnn"

    post_data = []
    for _img in images:
        base64_images = nparray2base64(_img)
        post_data.append({"img": base64_images})

    headers = {'Content-Type': 'application/json'}
    logger.info("请求crnn:%s", url)
    response = requests.post(url, json=post_data, headers=headers)
    logger.info("请求结果:%s", response.status_code)
    if response.content:
        result = response.json()
        logger.debug("crnn返回结果：%s", result)
    return result


class LsdLiner(object):
    def __init__(self, img):
        self.img = img
        self.h, self.w = img.shape[:2]

    def crop_subimg_by_template(self):
        name_img = self.img[int(self.h * 0.11):int(self.h * 0.24), int(self.w * 0.18):int(self.w * 0.4)]
        sex_img = self.img[int(self.h * 0.25):int(self.h * 0.35), int(self.w * 0.18):int(self.w * 0.25)]
        nation_img = self.img[int(self.h * 0.24):int(self.h * 0.34), int(self.w * 0.36):int(self.w * 0.50)]
        birthday_img = self.img[int(self.h * 0.35):int(self.h * 0.48), int(self.w * 0.18):int(self.w * 0.61)]
        address_img_1 = self.img[int(self.h * 0.48):int(self.h * 0.58), int(self.w * 0.17):int(self.w * 0.62)]
        address_img_2 = self.img[int(self.h * 0.58):int(self.h * 0.68), int(self.w * 0.17):int(self.w * 0.62)]
        address_img_3 = self.img[int(self.h * 0.68):int(self.h * 0.78), int(self.w * 0.17):int(self.w * 0.62)]
        idcard_img = self.img[int(self.h * 0.8):int(self.h * 0.91), int(self.w * 0.34):int(self.w * 0.93)]
        subimg = [name_img, sex_img, nation_img, birthday_img, address_img_1, address_img_2, address_img_3, idcard_img]
        logger.info('完成切图')

        for i, img in enumerate(subimg):
            cv2.imwrite('data/debug/' + '5subimg_' + str(i) + '.jpg', img)

        return subimg


# 多图识别
def recognize_img(subimg):  # 返回一个字典
    results = crnn(subimg)
    _res = [{'field': k, 'result': v} for k, v in results.items()]

    return _res


def main():
    path = "data/idcard/front/"
    files = os.listdir(path)
    i = 0
    results = []
    for file in files:
        logger.debug("处理文件%s", file)
        i += 1
        if i % 10 == 0:
            print("已处理数量：", i % 10)
        img = cv2.imread(os.path.join(path, file))
        if img is None:
            continue
        else:
            lsdLiner = LsdLiner(img)
            subimg = lsdLiner.crop_subimg_by_template()

            final_result = recognize_img(subimg)
            result_1 = analysis(final_result)
            results.append(result_1)

            # name, _ = os.path.splitext(file)
            with open("data/idcard/front_result.txt", "w", encoding='utf-8') as f:
                for res in results:
                    f.write(str(res) + "\n")

    return final_result


def analysis(result):
    res = result[0]['result']

    results = {
        "姓名": res[0]['word'],
        "性别": res[1]['word'].replace("民", "").replace("族", ""),
        "民族": res[2]['word'],
        "出生": res[3]['word'],
        "住址": res[4]['word'] + res[5]['word'] + res[6]['word'],
        "公民身份证号": res[7]['word']
    }
    return results


if __name__ == "__main__":
    init_logger()
    main()

# ceshi
# if __name__ == "__main__":
#
#     img = cv2.imread("data/correct/76E288F6-C89C-F15C-66CE-B48E667800C2B1-1.jpg")
#     #img = cv2.imread("data/correct/9.jpg")
#     #img = cv2.resize(img,(360,445))
#     print(img.shape)
#     lsdLiner = LsdLiner(img)
#     subimg = lsdLiner.crop_subimg_by_template()
#
#     final_result = recognize_subimg(subimg)
#     print(final_result)

'''
[ {'field': 'prism_wordsInfo', 
   'result': [{'word': '刘浩越'}, 
             {'word': '鹏'}, 
             {'word': '议'}, 
             {'word': '年十月10度'}, 
             {'word': '光泉南郭阑寝产雄菲巢'}, 
             {'word': '炒横加/)1驾'}, 
             {'word': ''}, 
             {'word': '440109209601164516'}]}, 
    {'field': 'sid', 'result': '202006242128828'}]

'''
