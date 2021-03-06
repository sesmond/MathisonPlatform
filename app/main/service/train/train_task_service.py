#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
训练任务管理

@author: vincent
@file:train_task_service.py
@time:2021/06/23
"""
import logging
import os
import signal

from app.main.db.db_tool import DBUtils
from app.main.entity.models import TProjectCase, TProject, TTrainTask
from app.main.utils import file_utils
from mathison.abstract_train_service import AbstractTrainService, TrainParam

logger = logging.getLogger(__name__)

train_service = None


def create_model(case: TProjectCase):
    """
    创建模型
    :param case:
    :return:
    """
    project_id = case.project_id
    if project_id is None:
        raise ValueError("项目不能为空！")
    db = DBUtils()
    project = db.get_by_id(TProject, project_id)
    # 创建
    # project:TProject
    print(project.project_url)
    train_path = "train"
    db.add(project)
    db.commit()


def start_train():
    # 1. 选择数据集
    # 校验数据集
    # 2. 训练GPU TODO 可以手动选，不选的时候进行自动调度

    # 3. 数据增强策略

    # 4. 测试集定义。

    # 5. 开始训练
    db = DBUtils()
    task = TTrainTask()
    # TODO 一个模型（case）一套代码吧，如果每次训练一套有点乱。
    # 如果每个project一套的话如果同时训练又怕互相干扰，还是放在项目里吧。
    db.add(task)
    db.commit()
    # TODO !! 不同模型的训练
    project_id = 1
    project = db.get_by_id(TProject, project_id)
    project: TProject
    project_url = project.project_url
    # TODO !! checkout 然后执行命令，然后就是项目内部的事情了，做好接口进行交互

    # 1. checkout
    # 项目存放路径
    prj_path = ""
    old_path = os.getcwd()
    file_utils.check_path(prj_path)
    # 2. 到项目内部，执行项目训练程序（传参），获取进程id
    train_path = ""
    os.chdir(train_path)
    # 切换工作目录
    real_train_cls = getattr()
    param = TrainParam()
    train_service = real_train_cls(param)
    train_service: AbstractTrainService
    signal.signal(signal.SIGUSR1, train_service.stop)
    train_service.start()
    # 训练结束后,恢复路径
    os.chdir(old_path)


def stop_train(task_id):
    db = DBUtils()
    task = db.get_by_id(TTrainTask, task_id)
    task: TTrainTask
    task.status
    pid = task.pid
    os.kill(pid, signal.SIGUSR1)


def handle_stop(signum, frame):
    print("当前项目id", os.getpid())
    print('Received and handle:', signum)
    train_service: AbstractTrainService
    train_service.stop()


if __name__ == '__main__':
    case = TProjectCase()
    case.project_id = 1
    create_model(case)
