# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.main.db.db_tool import DBUtils

Base = declarative_base()
metadata = Base.metadata


class TDataset(Base):
    __tablename__ = 't_dataset'
    __table_args__ = {'comment': '样本数据表'}

    id = Column(BigInteger, primary_key=True)
    dataset_id = Column(String(20), comment='数据集ID')
    sample_name = Column(String(100), comment='样本数据名')
    data_source = Column(String(20), comment='数据来源：本地文件/存储桶/其他')
    data_dir = Column(String(200), comment='数据地址')
    label_dir = Column(String(200), comment='标注地址')
    data_type = Column(String(20), comment='数据类型：img')
    label_type = Column(String(20), comment='标注类型：枚举类型')
    label_template = Column(String(20), comment='标注模板')
    entity_count = Column(BigInteger, comment='数据条数')
    status = Column(String(20), comment='状态：')
    create_time = Column(DateTime, comment='创建时间')
    creator = Column(String(20), comment='创建者')
    update_time = Column(DateTime, comment='更新时间')
    updater = Column(String(20), comment='更新人')


class TDatasetRecord(Base):
    __tablename__ = 't_dataset_record'
    __table_args__ = {'comment': '样本操作记录表'}

    id = Column(BigInteger, primary_key=True)
    dataset_id = Column(BigInteger, comment='数据集ID')
    sample_name = Column(String(100), comment='样本数据名')
    data_source = Column(String(20), comment='数据来源：本地文件/存储桶/其他')
    data_url = Column(String(200), comment='数据地址')
    label_url = Column(String(200), comment='标注地址')
    label_type = Column(String(20), comment='标注类型：枚举类型')
    label_format = Column(String(20), comment='标注格式：json/xml/txt等')
    entity_count = Column(BigInteger, comment='数据条数')
    status = Column(String(20), comment='状态：')
    create_time = Column(DateTime, comment='创建时间')
    creator = Column(String(20), comment='创建者')
    update_time = Column(DateTime, comment='更新时间')
    updater = Column(String(20), comment='更新人')



class TProject(Base):
    __tablename__ = 't_project'
    __table_args__ = {'comment': '训练项目表'}

    id = Column(BigInteger, primary_key=True)
    project_name = Column(String(100), comment='项目名称')
    project_url = Column(String(20), comment='项目地址：git地址')
    train_command = Column(String(100), comment='训练命令')
    create_time = Column(DateTime, comment='创建时间')
    creator = Column(String(20), comment='创建者')
    update_time = Column(DateTime, comment='更新时间')
    updater = Column(String(20), comment='更新人')


class TProjectCase(Base):
    __tablename__ = 't_project_case'
    __table_args__ = {'comment': '项目实例表'}

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, comment='项目id')
    project_name = Column(String(100), comment='项目名称')
    case_name_zh = Column(String(100), comment='用例中文名')
    case_name = Column(String(100), comment='用例英文名')
    create_time = Column(DateTime, comment='创建时间')
    creator = Column(String(20), comment='创建者')
    update_time = Column(DateTime, comment='更新时间')
    updater = Column(String(20), comment='更新人')


class TTrainTask(Base):
    __tablename__ = 't_train_task'
    __table_args__ = {'comment': '项目实例表'}

    id = Column(BigInteger, primary_key=True)
    project_case_id = Column(BigInteger, comment='项目用例Id')
    case_name = Column(String(100), comment='用例名')
    start_time = Column(DateTime, comment='任务开始时间')
    end_time = Column(DateTime, comment='任务结束时间')
    status = Column(String(20), comment='任务状态')
    create_time = Column(DateTime, comment='创建时间')
    creator = Column(String(20), comment='创建者')
    update_time = Column(DateTime, comment='更新时间')
    updater = Column(String(20), comment='更新人')


from sqlalchemy.orm import sessionmaker


def test1():
    engine = create_engine('mysql+mysqlconnector://test:a123456@localhost:3306/ocr?auth_plugin=mysql_native_password')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    d1 = TDataset()
    d1.sample_name = "测试项目名"
    # d1.id = 10
    xx  = session.add(d1)
    session.commit()
    print("成功插入")

if __name__ == '__main__':
    # test1()
    db = DBUtils()
    d1 = TDatasetRecord()
    d1.sample_name = "测试项目名2xxx"
    db.add(d1)
    db.commit()
    print(d1.id)
    db.flush()
