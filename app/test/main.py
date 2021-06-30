"""
程序入口：
先把功能入口在这列出来后续再分拆
"""

"""
1. 数据管理
"""
import sqlacodegen
# from
def create_dataset():
    """
    创建数据集
    :return:
    """
    while True:
        data_name = input("请输入数据集名称：")
        data_type = input("请输入数据类型：")
        print(data_name)
        print(data_type)
        break

if __name__ == '__main__':
    create_dataset()
#      sqlacodegen mysql://user:password@127.0.0.1:3306/ocr > models.py
# pip install mysql-connector
