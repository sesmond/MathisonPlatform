#!/usr/bin/python3
import logging

from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker, class_mapper

from app.main.db.db_pool import DBPool

logger = logging.getLogger(__name__)


class DBUtils(object):
    def __init__(self):
        Session = sessionmaker(bind=DBPool().conn)
        self.session = Session()

    # =====================================
    #  insert
    # =====================================
    def add(self, obj):
        res = self.session.add(obj)
        # last_insert_id = res.lastrowid
        return self

    # =====================================
    # batch insert
    # =====================================
    def add_all(self, objs=[]):
        res = self.session.add_all(objs)
        return self

    # =====================================
    # delete
    # =====================================
    def delete(self, obj, args=None):
        q = self.session.query(obj)
        if args:
            q = q.filter(*args)
        q.delete()
        logger.info(q)
        return self

    # =====================================
    # update
    # =====================================
    def update(self, obj, args, dict):
        q = self.session.query(obj).filter(*args)
        res = q.update(dict)
        return self

    # =====================================
    # query
    # =====================================
    def query(self, obj, args=None, order_by=None, page=None):
        q = self.session.query(*obj)
        if args:
            q = q.filter(*args)
        if order_by:
            q = q.order_by(*order_by)
        if page:
            q = q.slice(page[0], page[1])
        logger.info(str(q.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})))
        res = q.all()
        self.session.close()
        return res

    @staticmethod
    def convert_entity(obj):
        columns = [column.key for column in class_mapper(obj.__class__).columns]
        for c in columns:
            v = getattr(obj, c)
            if isinstance(v, bytearray):
                setattr(obj, c, v.decode('utf-8'))
        return obj

    def get_by_id(self, cls, id):
        """
        根据主键id查询（这里所有数据库主键约定为id）
        :param cls:
        :param id:
        :return:cls
        """
        res = self.session.query(cls).get(id)
        res = self.convert_entity(res)
        # q = self.session.query(*cls).filter_by(id=id)
        # res = q.one()
        return res

    # =====================================
    # rollback
    # =====================================
    def flush(self):
        self.session.flush()

    # =====================================
    # commit
    # =====================================
    def commit(self):
        self.session.commit()
        self.session.close()

    # =====================================
    # rollback
    # =====================================
    def rollback(self):
        self.session.rollback()
        self.session.close()
