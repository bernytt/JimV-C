#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request, redirect
import requests
from math import ceil


__author__ = 'James Iter'
__date__ = '2018/2/27'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'v_ssh_key',
    __name__,
    url_prefix='/ssh_key'
)

blueprints = Blueprint(
    'v_ssh_keys',
    __name__,
    url_prefix='/ssh_keys'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', None)

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

    ssh_keys_url = host_url + url_for('api_ssh_keys.r_get_by_filter')
    if keyword is not None:
        ssh_keys_url = host_url + url_for('api_ssh_keys.r_content_search')

    if args.__len__() > 0:
        ssh_keys_url = ssh_keys_url + '?' + '&'.join(args)

    ssh_keys_ret = requests.get(url=ssh_keys_url, cookies=request.cookies)
    ssh_keys_ret = json.loads(ssh_keys_ret.content)

    last_page = int(ceil(ssh_keys_ret['paging']['total'] / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    return render_template('ssh_keys_show.html', ssh_keys_ret=ssh_keys_ret,
                           page=page, page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        label = request.form.get('label')
        public_key = request.form.get('public_key', '')

        payload = {
            "label": label,
            "public_key": public_key
        }

        url = host_url + '/api/ssh_key'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        j_r = json.loads(r.content)
        if j_r['state']['code'] != '200':
            return render_template('failure.html',
                                   go_back_url='/ssh_keys',
                                   timeout=10000, title='添加失败',
                                   message_title='添加 SSH Key 失败',
                                   message=j_r['state']['sub']['zh-cn'])

        return render_template('success.html', go_back_url='/ssh_keys', timeout=10000, title='提交成功',
                               message_title='添加 SSH Key 的请求已被接受',
                               message='您所提交的 SSH Key 已创建。页面将在10秒钟后自动跳转到模板列表页面！')

    else:
        return redirect(url_for('v_ssh_keys.show'))

