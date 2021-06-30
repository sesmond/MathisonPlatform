import copy
import inspect
import json
import logging
import os
from json import JSONDecodeError

from app.main.app.bo.group_record_bo import GroupResult

logger = logging.getLogger(__name__)


def json_deserialize(json_data, obj, ignore_null=False):
    """
    反序列化为自定义对象
    :param json_data:
    :param obj:
    :param ignore_null: 如果json中不存在则忽略赋值，取对象默认值
    :return:
    """
    logger.debug("Got json data:%d bytes", len(json_data))
    try:
        data = json_data.decode('utf-8')
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        data = json.loads(data)
        if len(json_data) < 500:
            logger.info("参数：%r", data)
    except JSONDecodeError as e:
        logger.error("JSon数据格式错误:%r", data)
        raise Exception("JSon数据格式错误:" + str(e))
    if ignore_null:
        dic2class_ignore(data, obj)
    else:
        dic2class(data, obj)


#
def request2dict(request):
    str_data = request.get_data()
    data = str_data.decode('utf-8')
    try:
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        data = json.loads(data)
    except JSONDecodeError as e:
        logger.error(data)
        logger.error("JSon数据格式错误")
        raise Exception("JSon数据格式错误:" + str(e))
    return data


def dic2class(py_data, obj):
    """
    已经转成dict的数据转成自定义独享
    :param py_data: dict格式
    :param obj: 自定义对象
    :return:
    """
    for name in [name for name in dir(obj) if not name.startswith('_')]:
        if name not in py_data:
            setattr(obj, name, None)
        else:
            value = getattr(obj, name)
            setattr(obj, name, set_value(value, py_data[name]))


def dic2class_ignore(py_data, obj):
    """
    已经转成dict的数据转成自定义对象
    :param py_data: dict格式
    :param obj: 自定义对象
    :return:
    """
    for name in [name for name in dir(obj) if not name.startswith('_')]:
        if name not in py_data:
            # logger.debug("%r json中不存在，忽略，取默认值", name)
            # setattr(obj, name, obj.name)
            pass
        else:
            value = getattr(obj, name)
            setattr(obj, name, set_value(value, py_data[name], ignore_null=True))


def set_value(field_attr, dict_data, ignore_null=False):
    if str(type(field_attr)).__contains__('.') or isinstance(field_attr, type):

        full_args = inspect.getfullargspec(field_attr.__init__)
        if isinstance(field_attr, type):

            # 参数默认值
            if len(full_args.args) > 1:
                p = [""] * (len(full_args.args) - 1)

                new_obj = field_attr(*p)
            else:
                new_obj = field_attr()
        else:
            new_obj = field_attr
        # value 为自定义类
        if ignore_null:
            dic2class_ignore(dict_data, new_obj)
        else:
            dic2class(dict_data, new_obj)
    elif isinstance(field_attr, list):
        # value为列表
        if field_attr.__len__() == 0:
            # value列表中没有元素，无法确认类型
            new_obj = dict_data
        else:
            child_type = field_attr[0]

            # if isinstance(value[0], type):
            #     child_value_type = value[0]
            #
            # if isinstance(child_type, list):
            new_obj = []
            for child_py_data in dict_data:
                child_value = set_value(child_type, child_py_data)
                new_obj.append(child_value)
            # else:
            #     # value列表中有元素，以第一个元素类型为准
            #     if isinstance(value[0], type):
            #         child_value_type = value[0]
            #     else:
            #         child_value_type = type(value[0])
            #     value = []
            #     for child_py_data in py_data:
            #         child_value = child_value_type()
            #         child_value = set_value(child_value, child_py_data, ignore_null)
            #         value.append(child_value)


    else:
        new_obj = dict_data
    return new_obj


def obj2json(obj):
    """
    复杂结构转json
    :param obj:
    :return: dict结构
    """
    result = json.dumps(obj, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=False,
                        indent=4)
    return json.loads(result)


def obj2jsonStr(obj):
    """
    复杂结构转json
    :param obj:
    :return: dict结构
    """
    result = json.dumps(obj, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=False,
                        indent=4)
    return result


def print_json(data):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


def check_path(path):
    if not os.path.exists(path):
        print("路径不存在并创建：", path)
        os.makedirs(path)


def __remove_big_size_value(data):
    if type(data) == dict:
        for key, value in data.items():
            if type(value) == dict or type(value) == list:
                __remove_big_size_value(value)
            if type(value) == str and len(value) > 1000:
                data[key] = "{}......({})".format(value[:20], len(value))

    if type(data) == list:
        for i, v in enumerate(data):
            if type(v) == dict or type(v) == list:
                __remove_big_size_value(v)
            if type(v) == str and len(v) > 1000:
                data[i] = "{}......({})".format(v[:20], len(v))


# 用于提出尺寸比较大的json数据
def simple_dump(json_data):
    json_copy = copy.deepcopy(json_data)
    __remove_big_size_value(json_copy)
    return json_copy


def write_json(output_path, file_name, result):
    # 写 message
    pure_name = os.path.splitext(os.path.basename(file_name))[0]
    json_name = pure_name + ".json"
    json_path = os.path.join(output_path, json_name)
    check_path(output_path)
    with open(json_path, 'w', encoding='utf-8') as f1:
        json.dump(result, f1, ensure_ascii=False, default=lambda x: x.__dict__, sort_keys=False, indent=2)


def get_json_path(output_path, file_name):
    pure_name = os.path.splitext(os.path.basename(file_name))[0]
    json_name = pure_name + ".json"
    json_path = os.path.join(output_path, json_name)
    return json_path


def read_json(output_path, file_name):
    json_file = get_json_path(output_path, file_name)
    if os.path.exists(json_file):
        logger.debug("读取数据:%r", json_file)
        with open(json_file, 'r', encoding="utf-8") as f:
            result = json.load(f)
        return True, result
    else:
        logger.warning("无法找到json文件：%s", json_file)
        return False, None


def read(json_file):
    if os.path.exists(json_file):
        # logger.info("读取数据:%r", json_file)
        with open(json_file, 'r', encoding="utf-8") as f:
            result = json.load(f)
        return True, result
    else:
        return False, None


# python -m utils.json_utils
if __name__ == '__main__':
    data = "{'code': '0', 'message': 'success', 'result': [{'description': '转移登记', 'fields': [{'content': '杨芷和', 'description': '姓名/名称', 'key': 'name', 'prob': 1}, {'content': '居民身份证/370206195204064811', 'description': '身份证明名称/号码', 'key': 'code', 'prob': 1}, {'content': '购买', 'description': '获得方式', 'key': 'type', 'prob': 1}, {'content': '鲁0L68Y2', 'description': '机动车登记编号', 'key': 'plate', 'prob': 3}, {'content': '2015-12-17', 'description': '转移登记日期', 'key': 'date', 'prob': 1}], 'key': 'transfer_register'}, {'description': '转移登记', 'fields': [{'content': '丁操', 'description': '姓名/名称', 'key': 'name', 'prob': 1}, {'content': '居民身份证/342522199611163930', 'description': '身份证明名称/号码', 'key': 'code', 'prob': 1}, {'content': '购买', 'description': '获得方式', 'key': 'type', 'prob': 1}, {'content': '鲁B62A0X', 'description': '机动车登记编号', 'key': 'plate', 'prob': 1}, {'content': '2019-03-25', 'description': '转移登记日期', 'key': 'date', 'prob': 1}], 'key': 'transfer_register'}], 'sid': ''}"
    data = data.replace("'", "\"")
    data = json.loads(data)
    obj = GroupResult()
    dic2class(data, obj)

    print(obj.result)
    print(obj.result[0].fields)
    print(obj.result[1].fields)
