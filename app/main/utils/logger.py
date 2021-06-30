import logging
import os
import time

from app.main.app.utils.rotating_file_handler import SafeRotatingFileHandler


def init(dir,
         level=logging.DEBUG,
         when="D",
         backup=90,  # 保持90天
         _format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s"):
    train_start_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    filename = dir + '/ocr.log'
    print("日志文件：", filename)
    _dir = os.path.dirname(filename)
    if not os.path.isdir(_dir): os.makedirs(_dir)

    # 重新设置
    logger = logging.getLogger()
    logger.setLevel(level)
    print("设置日志等级：", level)

    formatter = logging.Formatter(_format)

    file_handler = SafeRotatingFileHandler(filename)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    print("设置日志文件输出方式：", filename, "/", level, "/", when, "/", backup)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    print("设置控制台输出方式")
    for l in logger.handlers:
        logger.info("当前日志系统的handler：%r", l)
