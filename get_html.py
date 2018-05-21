#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/21 14:04
# @Author  : caozhiye


import gzip
import json
import random
import urllib
from http import cookiejar
from urllib import parse
from urllib import request
from time import sleep
import datetime
import sys
import os
from bs4 import BeautifulSoup

# 登录URL
base_url = 'http://bbs.ngacn.cc/'
login_url = 'http://bbs.ngacn.cc/nuke.php?__lib=login&__act=login_ui'
user_base_url = "http://bbs.nga.cn/thread.php?authorid="

# Header信息字段
accept = r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
accept_language = r'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'  # 没变化一般不修改
accept_charset = r'utf-8;q=0.7,*;q=0.7'  # 没变化一般不修改
accept_encoding = r'gzip, deflate'  # 没变化一般不修改
content_type = r'application/x-www-form-urlencoded'  # 没变化一般不修改
connection = r'Keep-Alive'  # 没变化一般不修改

# user_agent没变化一般不需要修改
user_agent = r'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
cookie = r'your_cookie_string'


def get_cookie():
    """
    获取cookie对象
    :return: cookie对象
    """
    __cookie_filename = 'cookie.txt'  # cookie 保存文件名
    # cookie = cookiejar.CookieJar()
    __cookie = cookiejar.MozillaCookieJar(__cookie_filename)  # 声明一个CookieJar对象实例来保存cookie
    __cookie_handler = request.HTTPCookieProcessor(__cookie)
    # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
    return __cookie_filename, __cookie, __cookie_handler


def get_cookie_value(name):
    """
    根据cookie的name域查找对应的值
    :param name: cookie字段名称
    :return: cookie字段值
    """
    __cookie_filename, __cookie, __cookie_handler = get_cookie()
    __cookie.load(__cookie_filename, ignore_discard=True, ignore_expires=True)
    field_value = ""
    for item in __cookie:
        if item.name == name:
            field_value = item.value
            break
    return field_value


def read_cookie_string_file():
    cookie_file = "cookie_string.txt"
    f = open(cookie_file, 'r', encoding="utf-8")
    cookie_line = ""
    for line in f.readlines():
        cookie_line = cookie_file + line.strip()
        # print(cookie_line)
    return cookie_line


def get_user_topic_page(userid):
    """
    登陆后访问用户主题页面
    :param userid: 用户id
    :return: html页面 
    """
    __cookie_filename, __cookie, __cookie_handler = get_cookie()

    head = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
        'Cookie': read_cookie_string_file()
    }

    get_url = user_base_url + userid
    opener = request.build_opener(__cookie_handler)  # 通过CookieHandler创建opener
    req1 = request.Request(url=get_url, headers=head, method='GET')  # 创建Request对象
    __response = opener.open(req1)

    __cookie.save(__cookie_filename, ignore_discard=True, ignore_expires=True)

    result = __response.read()  # 从response对象读取result结果二进制流
    html_byte = gzip.decompress(result)
    # import chardet
    # detect_result = chardet.detect(html_byte)
    # print(detect_result)
    html = html_byte.decode("gbk")
    # print(html)
    return html


def get_user_topic_dict(userid):
    html = get_user_topic_page(userid)
    bs = BeautifulSoup(html, 'html.parser')

    topic_tag_list = bs.select('a[class="topic"]')  # 主题
    topic_list = []
    for item in topic_tag_list:
        topic_list.append(item.string)
    # debug
    print(len(topic_list))
    print(topic_list)  # 用户一页35个帖子

    topic_url_list = []
    for item in topic_tag_list:
        topic_url_list.append("http://bbs.nga.cn" + item.get("href"))
    print(topic_url_list)

    topic_time_tag_list = bs.select('span[class="silver postdate"]')  # unix 时间戳
    topic_time_list = []
    for item in topic_time_tag_list:
        topic_time_list.append(item.string)
    print(topic_time_list)


if __name__ == '__main__':
    get_user_topic_dict("1607961")
    # get_user_topic_page("1607961")
    # read_cookie_string_file()
