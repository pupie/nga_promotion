#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/21 14:04
# @Author  : caozhiye


import datetime
import gzip
import operator
import sys
import time
from http import cookiejar
from time import sleep
from urllib import parse
from urllib import request

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


def timestamp_datetime(value):
    """
    将unix时间戳转换成可读格式
    :param value:
    :return:
    """
    date_format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    # 经过localtime转换后变成
    # time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(date_format, value)
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
    """
    从文件读取cookie数据用以登录
    :return: cookie字符串
    """
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

    get_url = user_base_url + str(userid)
    # print (get_url)
    html = ""
    try:
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
    except Exception as e:
        print("!!!Error in reading user topic page!!!:", e)

    # print("html=", html)
    return html


def get_user_topic_lists(userid):
    """
    从WEB读取用户主题列表，主题URL，主题发布时间
    :param userid: 用户ID
    :return: 返回用户主题列表，主题URL，主题发布时间
    """
    print("get user topic list from web...")
    html = get_user_topic_page(userid)
    if html == "":
        username = "网络异常"
        topic_list, topic_url_list, topic_time_list = read_user_list_from_file(userid)
        return username, topic_list, topic_url_list, topic_time_list

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
    file_name = str(userid) + ".txt"
    f = open(file_name, 'w+')
    for i in range(0, len(topic_list) - 1):
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
    f.close()
    return username, topic_list, topic_url_list, topic_time_list


def read_user_list_from_file(userid):
    """
    读取文件用户主题列表，主题URL，主题发布时间
    :param userid: 用户ID
    :return: 返回用户主题列表，主题URL，主题发布时间
    """
    file_name = str(userid) + ".txt"
    try:
        open(file_name, 'r')
    except FileNotFoundError:
        print("No user file found, will create one.")
        save_user_list_to_file(userid)
        print("New user topic list saved!")

    f = open(file_name, 'r')
    get = f.read()
    topic_list = []
    topic_url_list = []
    topic_time_list = []
    # topic_time_list = []
    try:
        line_list = get.split("\n")
        topic_list = line_list[0].split("\t")
        topic_url_list = line_list[1].split("\t")
        topic_time_list = line_list[2].split("\t")
        topic_time_list = [int(x) for x in topic_time_list]
    except Exception as e:
        print("Error in reading list from file!!!:", e)
    f.close()
    # debug
    print("read user topic list from file...")
    # print(topic_list)
    # print(topic_url_list)
    # print(topic_time_list)
    return topic_list, topic_url_list, topic_time_list


def check_if_new_topic(userid_list):
    """
     检查该用户是否有新主题发布
    :param userid_list: 用户ID
    :return: 布尔值
    """
    new_topic = None
    for userid in userid_list:
        print("start check user topic for user:", userid)
        r_topic_list, r_topic_url_list, r_topic_time_list = read_user_list_from_file(userid)
        username, g_topic_list, g_topic_url_list, g_topic_time_list = save_user_list_to_file(userid)
        g_time_list = sorted(g_topic_time_list, reverse=True)
        r_time_list = sorted(r_topic_time_list, reverse=True)
        # debug
        # print("compare lists:")
        # print(g_time_list)
        # print(r_time_list)

        if operator.eq(g_time_list, r_time_list):
            new_topic = False
            print("...No new topic...")
        else:
            new_topic = True
            print("===New topic found===")
            break
    return new_topic


def format_push_message(userid_list):
    """
    格式化推送消息主体
    :param userid_list: 用户ID列表
    :return:消息主体
    """
    username_list = []
    message_markdown_all = ""
    print("formatting markdown message:")
    for user in userid_list:
        username, g_topic_list, g_topic_url_list, g_topic_time_list = get_user_topic_lists(user)
        message_markdown = ""
        message_body_head = "用户" + "\"" + username + "\"" + "的最近的10个帖子为：" + "\n"
        for i in range(0, 10):
            message_markdown = message_markdown + "1. " + "[" + g_topic_list[i] + "]" + "(" + g_topic_url_list[
                i] + ")" + "\t" + "\t" + timestamp_datetime(g_topic_time_list[i]) + "\n"

        message_markdown = message_body_head + message_markdown
        username_list.append(username)
        message_markdown_all = message_markdown_all + message_markdown + "\n" + "\n"

    print(username_list)
    print(message_markdown_all)
    return username_list, message_markdown_all


def get_key_from_file(filename):
    """
    从文件读取推送秘钥
    :param filename: 文件名
    :return:秘钥
    """
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
    """
    一对一推送新消息至serverchan
    :param userid: 用户id
    :return:
    """
    serverchan_sckey = get_key_from_file("serverchan_key")
    username_list, message = format_push_message(userid)
    username_string = ""
    for username in username_list:
        username_string = username_string + username + "，"
    username_string = username_string[:-1]
    # print(username_string)

    # https://sc.ftqq.com/SCUxxxxxxxxxxxxxxxxxxxxxxxxxxxx.send
    post_url = "https://sc.ftqq.com/" + serverchan_sckey + ".send"
    # print(post_url)

    post_data = {
        'text': "您关注的用户：" + "\"" + username_string + "\"" + "有新帖子啦！",
        'desp': message
    }

    head = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
    }

    print("Pushing messages to serverchan...")
    get_config_post_data = parse.urlencode(post_data).encode('utf-8')  # 使用urlencode方法转换标准格式
    req1 = request.Request(url=post_url, data=get_config_post_data, headers=head, method='POST')  # 创建Request对象
    resp1 = request.urlopen(req1)
    # html = resp1.read().decode('utf-8')


def push_new_message_pushbear(userid):
    """
    一对多推送新消息至pushbear
    :param userid: 用户id
    :return:
    """
    pushbear_sckey = get_key_from_file("pushbear_key")
    username_list, message = format_push_message(userid)
    username_string = ""
    for username in username_list:
        username_string = username_string + username + "，"
    username_string = username_string[:-1]

    # https://pushbear.ftqq.com/sub?sendkey={sendkey}&text={text}&desp={desp}
    post_url = "https://pushbear.ftqq.com/sub"
    print(post_url)

    post_data = {
        'sendkey': pushbear_sckey,
        'text': "您关注的用户：" + "\"" + username_string + "\"" + "有新帖子啦！",
        'desp': message
    }

    head = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
    }
    print("Pushing messages to pushbear...")
    get_config_post_data = parse.urlencode(post_data).encode('utf-8')  # 使用urlencode方法转换标准格式
    req1 = request.Request(url=post_url, data=get_config_post_data, headers=head, method='POST')  # 创建Request对象
    resp1 = request.urlopen(req1)


def read_user_form_file(user_file):
    """
    从文件读取关注的用户列表
    :param user_file: 文件名，每一个用户ID占一行
    :return:用户ID数值列表
    """
    file_name = user_file + ".txt"
    try:
        open(file_name, 'r')
    except FileNotFoundError:
        print("!!!No list file found!!!")

    f = open(file_name, 'r')
    get = f.read()
    user_list = get.split("\n")
    while '' in user_list:
        user_list.remove('')

    user_list = [int(x) for x in user_list]
    f.close()
    print(user_list)
    return user_list


def start_job(user_file):
    """
    开始检测任务
    :param user_file: 用户文件
    :return:
    """
    while 1:
        ctime = datetime.datetime.now()
        hour = ctime.hour
        minute = ctime.minute
        second = ctime.second
        stime = str(ctime)
        # sys.stdout.write(stime + '\n')
        # sys.stdout.flush()
        # sleep(0.1)
        # os.system('cls')
        # print(second)
        # if second == 0:
        if minute % 2 == 0 and second == 0:
            sleep(3)
            sys.stdout.write(stime + "\t")
            print("start checking user topics...")
            user_list = read_user_form_file(user_file)
            if_new_topic = check_if_new_topic(user_list)
            # print(if_new_topic)
            if if_new_topic:
                push_new_message_serverchan(user_list)
                sleep(3)
                push_new_message_pushbear(user_list)


if __name__ == '__main__':
    start_job("nga_user")

    # 蓝湖1607961， 燃灯122698
    # check_if_new_topic((1607961, 122698))
    # get_user_topic_lists("1607961")
    # save_user_list_to_file("1607961")
    # read_user_list_from_file("1607961")
    # check_if_new_topic((1607961, 122698))
    # format_push_message((1607961, 122698))
    # push_new_message_serverchan((1607961, 122698))
    # push_new_message_pushbear((1607961, 122698))
