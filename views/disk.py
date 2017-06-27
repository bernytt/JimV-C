#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil
import re


__author__ = 'James Iter'
__date__ = '2017/6/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_disk',
    __name__,
    url_prefix='/disk'
)

blueprints = Blueprint(
    'v_disks',
    __name__,
    url_prefix='/disks'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', None)
    resource_path = request.path

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    if order_by is not None:
        args.append('order_by=' + order_by)

    if order is not None:
        args.append('order=' + order)

    host_url = request.host_url.rstrip('/')

    disks_url = host_url + url_for('api_disks.r_get_by_filter')
    if keyword is not None:
        disks_url = host_url + url_for('api_disks.r_content_search')

    if args.__len__() > 0:
        disks_url = disks_url + '?' + '&'.join(args)

    disks_ret = requests.get(url=disks_url)
    disks_ret = json.loads(disks_ret.content)

    last_page = int(ceil(disks_ret['paging']['total'] / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page:
                break

    return render_template('disk_show.html', disks_ret=disks_ret, resource_path=resource_path, page=page,
                           page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        size = request.form.get('size')
        quantity = request.form.get('quantity')
        remark = request.form.get('remark')

        payload = {
            "size": int(size),
            "quantity": int(quantity),
            "remark": remark
        }

        url = host_url + '/api/disk'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        return render_template('success.html', go_back_url='/disks', timeout=10000, title='提交成功',
                               message_title='创建实例的请求已被接受',
                               message='您所提交的资源正在创建中。根据所提交资源的数量，需要等待几到十几秒钟。页面将在10秒钟后自动跳转到实例列表页面！')

    else:
        return render_template('disk_create.html')


