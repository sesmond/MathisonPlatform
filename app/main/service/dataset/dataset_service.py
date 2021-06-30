#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
数据集管理相关服务
@author: vincent
@file:dataset_service.py
@time:2021/06/22
"""
import logging

from app.main.db.db_tool import DBUtils
from app.main.entity.models import TDataset, TDatasetRecord

logger = logging.getLogger(__name__)


class BaseDatasetService:
    def __init__(self):
        pass


class ImageDatasetService(BaseDatasetService):
    pass


def create(dataset: TDataset):
    """
    新增数据集
    :param dataset:
    :return:
    """
    if dataset.sample_name is None:
        raise ValueError("样本名不能为空！")

    data_type = dataset.data_type
    if data_type == "img":
        pass
        # TODO 数据导入 是创建数据集的时候导入还是怎么着？
        data_service = ImageDatasetService()
        dataset.label_type
        dataset.label_template
    else:
        raise ValueError("数据类型不正确！")

    db = DBUtils()
    db.add(dataset)
    db.commit()
    # TODO 回滚什么的暂时没加


def import_data(record: TDatasetRecord):
    """
     数据集导入数据
    :param record:
    :return:
    """
    # 导入数据 record
    data_source = record.data_source
    if data_source == "local":
        record.data_dir
    else:
        pass
    db = DBUtils()
    db.add(record)
    db.commit()


if __name__ == '__main__':
    import_data(None)
