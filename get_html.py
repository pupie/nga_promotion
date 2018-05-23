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
import time
from time import sleep
import datetime
import sys
import os
from bs4 import BeautifulSoup
import operator

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


def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    # 经过localtime转换后变成
    # time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    # print(dt)
    return dt


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


def get_user_topic_lists(userid):
    """
    从WEB读取用户主题列表，主题URL，主题发布时间
    :param userid: 用户ID
    :return: 返回用户主题列表，主题URL，主题发布时间
    """
    print("get user topic list from web:")
    html = get_user_topic_page(userid)
    bs = BeautifulSoup(html, 'html.parser')

    username_tag_list = bs.select('a[class="author"]')  # 用户名
    username = username_tag_list[0].string
    print(username)

    topic_tag_list = bs.select('a[class="topic"]')  # 主题
    topic_list = []
    for item in topic_tag_list:
        topic_list.append(item.string)
    # debug
    # print(len(topic_list))
    print(topic_list)  # 用户一页35个帖子

    topic_url_list = []
    for item in topic_tag_list:
        topic_url_list.append("http://bbs.nga.cn" + item.get("href"))
    print(topic_url_list)

    topic_time_tag_list = bs.select('span[class="silver postdate"]')  # unix 时间戳
    topic_time_list = []
    for item in topic_time_tag_list:
        topic_time_list.append(int(item.string.strip()))
    print(topic_time_list)

    return username, topic_list, topic_url_list, topic_time_list


def save_user_list_to_file(userid):
    """
    保存用户主题列表，主题URL，主题发布时间到文件
    :param userid: 用户ID
    """
    username, topic_list, topic_url_list, topic_time_list = get_user_topic_lists(userid)
    file_name = userid + ".txt"
    f = open(file_name, 'w+')
    for i in range(0, len(topic_list) - 1):
        # f.write(topic_list[i].strip() + "\t" + topic_url_list[i].strip() + "\t" + topic_time_list[i].strip() + "\n")
        f.write(topic_list[i].strip() + "\t")
    f.write(topic_list[-1])
    f.write("\n")

    for i in range(0, len(topic_url_list) - 1):
        f.write(topic_url_list[i].strip() + "\t")
    f.write(topic_url_list[-1])
    f.write("\n")

    for i in range(0, len(topic_time_list) - 1):
        f.write(str(topic_time_list[i]) + "\t")
    f.write(str(topic_time_list[-1]))
    f.write("\n")
    f.close


def read_user_list_from_file(userid):
    """
    读取文件用户主题列表，主题URL，主题发布时间
    :param userid: 用户ID
    :return: 返回用户主题列表，主题URL，主题发布时间
    """
    file_name = userid + ".txt"
    try:
        open(file_name, 'r')
    except FileNotFoundError:
        save_user_list_to_file(userid)

    f = open(file_name, 'r')
    get = f.read()
    line_list = get.split("\n")
    topic_list = line_list[0].split("\t")
    topic_url_list = line_list[1].split("\t")
    topic_time_list = line_list[2].split("\t")
    topic_time_list = [int(x) for x in topic_time_list]
    f.close()
    # debug
    print("read user topic list from file:")
    print(topic_list)
    print(topic_url_list)
    print(topic_time_list)
    return topic_list, topic_url_list, topic_time_list


def check_if_new_topic(userid):
    """
     检查该用户是否有新主题发布
    :param userid: 用户ID
    :return: 布尔值
    """
    username, g_topic_list, g_topic_url_list, g_topic_time_list = get_user_topic_lists(userid)
    r_topic_list, r_topic_url_list, r_topic_time_list = read_user_list_from_file(userid)
    g_time_list = sorted(g_topic_time_list, reverse=True)
    r_time_list = sorted(r_topic_time_list, reverse=True)
    # debug
    # print("compare lists:")
    # print(g_time_list)
    # print(r_time_list)

    if operator.eq(g_time_list, r_time_list):
        new_topic = False
        print("No new topic.")
    else:
        new_topic = True
        print("New topic found!")

    return new_topic


def format_push_message(userid):
    username, g_topic_list, g_topic_url_list, g_topic_time_list = get_user_topic_lists(userid)

    print("formatting markdown message:")
    message_markdown = ""
    message_body_head = "该用户的最近的10个帖子为：" + "\n"
    for i in range(0, 10):
        message_markdown = message_markdown + "1. " + "[" + g_topic_list[i] + "]" + "(" + g_topic_url_list[
            i] + ")" + "\t" + "\t" + timestamp_datetime(g_topic_time_list[i]) + "\n"

    message_markdown = message_body_head + message_markdown
    print(message_markdown)

    return username, message_markdown


def get_key_from_file(filename):
    file = filename + ".txt"
    f = open(file, 'r')
    get = f.read()
    line_list = get.split("\n")
    serverchan_sckey = line_list[0].strip()
    f.close()
    # debug
    # print("serverchan key:", serverchan_sckey)
    return serverchan_sckey


def push_new_message_serverchan(userid):
    serverchan_sckey = get_key_from_file("serverchan_key")
    username, message = format_push_message(userid)
    # https://sc.ftqq.com/SCUxxxxxxxxxxxxxxxxxxxxxxxxxxxx.send
    post_url = "https://sc.ftqq.com/" + serverchan_sckey + ".send"
    print(post_url)

    post_data = {
        'text': "用户" + "\"" + username + "\"" + "有新帖子啦！",
        'desp': message
    }

    head = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
    }

    get_config_post_data = parse.urlencode(post_data).encode('utf-8')  # 使用urlencode方法转换标准格式
    req1 = request.Request(url=post_url, data=get_config_post_data, headers=head, method='POST')  # 创建Request对象
    resp1 = request.urlopen(req1)
    # html = resp1.read().decode('utf-8')


def push_new_message_pushbear(userid):
    pushbear_sckey = get_key_from_file("pushbear_key")
    username, message = format_push_message(userid)
    # https://pushbear.ftqq.com/sub?sendkey={sendkey}&text={text}&desp={desp}
    post_url = "https://pushbear.ftqq.com/sub"
    print(post_url)

    post_data = {
        'sendkey': pushbear_sckey,
        'text': "用户" + "\"" + username + "\"" + "有新帖子啦！",
        'desp': message
    }

    head = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
    }

    get_config_post_data = parse.urlencode(post_data).encode('utf-8')  # 使用urlencode方法转换标准格式
    req1 = request.Request(url=post_url, data=get_config_post_data, headers=head, method='POST')  # 创建Request对象
    resp1 = request.urlopen(req1)



if __name__ == '__main__':
    # 蓝湖1607961， 燃灯122698
    # get_user_topic_lists("1607961")
    # save_user_list_to_file("1607961")
    # read_user_list_from_file("1607961")
    # check_if_new_topic("1607961")
    format_push_message("1607961")
    # push_new_message_serverchan("1607961")
    # push_new_message_pushbear("1607961")
