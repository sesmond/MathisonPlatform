"""
这个类，抽取，对调试图像的一些工具函数，
发现这类函数常用，所以，抽取出来
"""
import cv2
# from ocr.vo.bo.bbox import BBox
import numpy as np

COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)


def draw_rect(image, boxes, draw=False):
    if not draw:
        return None
    if len(boxes) == 0:
        return image
    for box in boxes:
        box = box.astype(np.int32)
        cv2.rectangle(image,
                      (box[0], box[1]),
                      (box[2], box[3]),
                      color=COLOR_GREEN,
                      thickness=1)
    return image


# box [[x1,y1],[x2,y2],....]
def draw_box(image, box, color=COLOR_RED, thickness=1):
    draw_box = np.array(box).reshape((-1, 2))
    cv2.polylines(image, np.int32([draw_box]), color=color, thickness=thickness, isClosed=True)


# box [2,2]
def draw_rect(image, pt1, pt2, color=COLOR_RED, thickness=1):
    cv2.rectangle(image, pt1, pt2, color=color, thickness=thickness)


# rects: [N,2,2]
def draw_rects(image, rects, color=COLOR_RED, thickness=1):
    for rect in rects:
        print(rect)
        x1 = int(rect[0])
        y1 = int(rect[1])
        x2 = int(rect[2])
        y2 = int(rect[3])
        draw_rect(image, (x1, y1), (x2, y2), color=color, thickness=thickness)


# 在图上画2点的矩形框
def draw_boxes(image, boxes, color=COLOR_RED):
    """
    @param image: 要画的图片
    @param boxes:  应该是n,4,2格式
    @param color:
    @return:
    """
    # TODO 随机选一个颜色
    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            draw_box(image, box, thickness=2, color=color)
    return image


# def draw_bboxes(image, bboxes):

# 画poses[['x':1212,'y':1212],['x':1212,'y':1212],['x':1212,'y':1212],['x':1212,'y':1212]].....
def draw_xy_poses(image, poses, color=COLOR_RED, thickness=2):
    # 在原图上，画出卡片的位置
    poses = [[xy['x'], xy['y']] for xy in poses]
    poses = np.array(poses)
    draw_pos(image, poses, color=color, thickness=thickness)


def draw_pos(image, pos, color=COLOR_RED, thickness=1):
    return draw_poses(image, [pos], color, thickness)


def draw_poses(image, poses, color=COLOR_RED, thickness=1):
    boxes = np.array(poses).astype(np.int32)
    cv2.polylines(image, boxes, isClosed=True, color=color, thickness=thickness)
    return image


# python -m ocr.utils.image_debug_utils
if __name__ == "__main__":
    image_path = "test/images/test_bank.jpg"
