# encoding:utf-8
# !/usr/bin/python3

import json
import os

import cv2


def modify_filename(json_path):
    with open(json_path, "r") as f:
        json_data = json.load(f)
        new_shapes = []
        for category in json_data['shapes']:
            new_label = {
                "label": 'id-1',
                "points": category['points'],
                "shape_type": category['shape_type']
            }
            new_shapes.append(new_label)

        new_json = {
            "version": json_data["version"],
            "flags": json_data["flags"],
            "shapes": new_shapes,
            "imagePath": json_data["imagePath"],
            "imageData": json_data["imageData"],
            "imageHeight": json_data["imageHeight"],
            "imageWidth": json_data["imageWidth"]
        }
    return new_json


def main(old_dir, new_dir):
    if not (os.path.exists(new_dir)):
        os.makedirs(new_dir)

    files = os.listdir(old_dir)
    for file in files:
        filename, ext = os.path.splitext(file)
        if ext != ".jpg":
            continue
        else:
            img_path = os.path.join(old_dir, file)
            print(img_path)
            json_path = os.path.join(old_dir + file[:-4] + ".json")
            img = cv2.imread(img_path)
            print(img.shape)

            new_img_path = os.path.join(new_dir + file)
            cv2.imwrite(new_img_path, img)
            new_json = modify_filename(json_path)
            new_json_path = os.path.join(new_dir + file[:-4] + ".json")
            with open(new_json_path, "w", encoding='utf-8') as g:
                json.dump(new_json, g, indent=2, sort_keys=True, ensure_ascii=False)


if __name__ == "__main__":
    old_dir = "data/djz/labelme_split/"
    new_dir = "data/djz/new_labelme_split/"

    main(old_dir, new_dir)
