#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
所有训练类的基类，用于定义训练方式
@author: vincent
@file:abstract_train_service.py
@time:2021/07/07
"""

import abc


class TrainParam(object):
    """
    训练参数
    """
    # 日志路径
    log_path = ""
    # 模型保存路径
    model_path = ""
    # tesnorboard 保存路径
    tboard_path = ""


class AbstractTrainService(metaclass=abc.ABCMeta):
    def __init__(self, param: TrainParam):
        # 训练需要的参数
        self.param = param

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
