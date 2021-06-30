#!/usr/bin/python3
from sqlalchemy import create_engine


class Config:
    # 数据库信息
    DB_TEST_HOST = "localhost"
    DB_TEST_PORT = 3306
    DB_TEST_NAME = "ocr"
    DB_TEST_USER = "test"
    DB_TEST_PASSWORD = "a123456"
    # 数据库连接编码
    DB_CHARSET = "utf8"
    # 连接池初始大小
    DB_POOL_SIZE = 10
    # 超过连接池大小,最多创建的连接
    DB_MAX_OVERFLOW = 10
    # 获取不到连接最大等待时间
    DB_POOL_TIMEOUT = 30
    # 多长时间回收线程池中连接（重置）
    DB_POOL_RECYCLE = -1


class DBPool(object):
    """
    数据库连接池
    """
    ___pool = None

    def __init__(self):
        self.conn = self.__get_mysql_conn()

    def __get_mysql_conn(self):
        if self.___pool is None:
            # "mysql+mysqlconnector://root:password@localhost:3306/test"
            db_url = "mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=%s&auth_plugin=mysql_native_password" % (
                Config.DB_TEST_USER, Config.DB_TEST_PASSWORD, Config.DB_TEST_HOST, Config.DB_TEST_PORT,
                Config.DB_TEST_NAME, Config.DB_CHARSET)
            self.___pool = create_engine(
                db_url,
                max_overflow=Config.DB_MAX_OVERFLOW,
                pool_size=Config.DB_POOL_SIZE,
                pool_timeout=Config.DB_POOL_TIMEOUT,
                pool_recycle=Config.DB_POOL_RECYCLE
            )
        return self.___pool
