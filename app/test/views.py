#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim:fenc=utf-8
# @author tlwlmy
# @version 2017-03-06

from app.test import test
from app.common.functions import api_response, save_stream_img, md5
from app.module.task_celery import task_celery
from app.common.constant import *
from app.datasource import s3
from config import AWS

@test.route('/user_inform', methods=['GET'])
def user_inform():
    # 测试通知用户信息

    message = {
        'uid': 1,
        'inform': u'Hello Word!',
    }

    from app.task.user import user_inform
    message = user_inform(message)
    # message = task_celery.send_user_inform(message)

    return api_response(message)

@test.route('/save_image', methods=['GET'])
def save_image():
    """
    保存图片
    """

    import base64, os
    prefix = 'data:image/png;base64,'

    # 读图片数据
    filename = os.path.join(CM_STATIC_PATH, 'images/img.png')
    fp = open(filename, 'rb')
    data = prefix + base64.b64encode(fp.read()).decode('utf-8')

    params = {
        'input': {
            'type': PICTURE_TYPE_PNG,
            'file': 'wechat',
            'icon': data,
        }
    }

    # 查询路径
    path = AWS['s3_buckets']['wxiao'][params['input']['file']]['path']
    icon_name = md5(params['input']['icon'])

    if params['input']['type'] == PICTURE_TYPE_PNG:
        # 生产文件名
        icon_name = '{0}.png'.format(icon_name)
    elif params['input']['type'] == PICTURE_TYPE_GIF:
        # 生产文件名
        icon_name = '{0}.gif'.format(icon_name)
    elif params['input']['type'] == PICTURE_TYPE_JPG:
        # 生产文件名
        icon_name = '{0}.jpg'.format(icon_name)

    # 文件路径名
    icon_name = '{0}/{1}'.format(path, icon_name)

    # 文件路径名
    filename = 'images/{0}'.format(icon_name)

    # 保存图片
    icon = base64.b64decode(params['input']['icon'][22:])  # 去掉前面23个字符的标示符
    target = save_stream_img(filename, icon)

    # 打开文件
    fp = open(target, 'rb')
    s3.Bucket(AWS['s3_buckets']['wxiao']['name']).put_object(Key=icon_name, Body=fp)

    return api_response({'c': 0})
