#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-29 10:11
# @email    : rancho941110@gmail.com

'''获取所有注册用户的主页链接
features:
- 统一编码
- 不区分数字和字母, 两者同时爬
- 实时进度条显示, 形象直观
- 记忆功能, 自动续爬

- 08.10优化日志信息
- 08.08生成器代替while循环
其他: 去掉了随机agent(测试发现直接发包没问题)

todo:
- * 多线程模型
'''

import sys
import json
import requests
from time import clock
from timeit import default_timer
from datetime import datetime
from itertools import dropwhile

class Directory(object):
    """遍历目录"""
    def __init__(self, index):
        # 一些常量
        self.base = 'http://www.linkedin.com/directory/people-'
        self.split = '-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'
        self.sub = []
        self.count = 0                          # 记录发包次数
        self.alphabet = [i for i in range(1, 27)]
        self.numrange = [i for i in range(1, 101)]

        # share lock!
        self.url = ''                           # 发请求包时的url
        self.result = []                        # 页面解析后含有refer的列表
        self.index = index
        # self.flag = False                       # 目录尾部404标志

    # 用生成器代替原有的while循环
    # 新特性: 代理迭代, 迭代目录与发包请求异步进行
    # 不变特性: 自动恢复(迭代跃进), 终止检测(需要bool flag配合来完成)
    def generator(self):
        for init in self.alphabet:
            for page in self.numrange:
                for line in self.numrange:
                    non_item = init, page, line
                    yield non_item
                    for rank in self.numrange:
                        lan_item = init, page, line, rank
                        yield lan_item
                        # if self.flag:
                        #     line += 1
                        #     break

    def start_traverse(self):
        history = tuple(self.index)
        gen = self.generator()
        for sub in dropwhile(lambda sub: sub != history, gen):
            self.sub = sub
            write_index(sub)
            # sleep(0.01)
            if len(sub) == 4:
                sub = list(sub)
                sub[0] = chr(sub[0] + 96)

            # GET PAGE
            current = sub[-1]
            str_sub = map(lambda x: str(x), sub)
            self.url = self.base + self.split.join(str_sub)
            # push to work queue
            if self.get_page(self.url):
                # 得到相应页面后的操作, 解析出主页链接并保存
                self.parse(self.response)
                self.save_tofile()
                self.count += 1         # 统计发包数(不计404)
                print self.url          # 打印已存好的 url
                self.printBar(str_sub, current)
            else:
                continue

    def get_page(self, url):
        self.response = requests.get(self.url)
        if self.response.status_code == 200:
            return True
        elif self.response.status_code == '404':
            return False
        else:
            # write to log
            return False

    def parse(self, text):
        from lxml import etree
        selector = etree.HTML(text.content)
        self.result = selector.xpath(self.pattern)

    def save_tofile(self):
        with open('1', 'a+') as f:
            for item in self.result:
                if isinstance(item, str):
                    f.write(item)
                elif isinstance(item, unicode):
                    f.write(item.encode('utf8'))
                else:
                    print "@@@@@@@@@\n\n\ncan't encode!!!"
                    raise UnicodeEncodeError
                f.write('\n')

    def printBar(self, pre, current):
        percent = current / 5
        print " " * 18,
        print self.split.join(pre),
        bar_str = '[' + '#' * percent + ' ' * (20 - percent) + ']' + '\r'

        # sys.stdout.write(str(current))
        sys.stdout.write(bar_str)
        sys.stdout.flush()

def write_index(data):
    """当前记录写入json"""
    with open('index.json', 'w') as f:
        json.dump(data, f)

def load_index():
    """从json导入历史位置"""
    re = []
    with open('index.json', 'r') as f:
        data = json.load(f)
    for item in data:
        re.append(item)
    return re

def timelogging(func):
    def wrapper():
        s = (edate - sdate).total_seconds()
        c = clock()
        r = default_timer() - start
        p = (1 - c / r) * 100
        print "START at %32s"               % sdate
        print "ENDED at %32s"               % edate
        print "RUN time used: %26.3f"       % s
        print "PRO time used: %26.3f "      % r
        print "CPU time used: %26.3f"       % c
        print "IO  time used: %25.3f%%"     % p
        if test.count:
            petime = test.count / r
            print "Requests page: %26d"     % test.count
            print "Average  rate: %24.3f/s" % petime
        print
        print "exit, see you..."
        return func()
    return wrapper

@timelogging
def quit():
    sys.exit()

if __name__ == '__main__':
    start = default_timer()
    sdate = datetime.now()
    while True:
        try:
            origin = load_index()   # 从json读历史记录, 要指定起始位置可以直接改json
            print "recover from ", origin
            test = Directory(origin)
            test.start_traverse()
        except requests.exceptions.ConnectionError, e:
            print "WRONG: ", e
            print "continue..."
            continue
        except requests.exceptions.ReadTimeout, e:
            print "WRONG: ", e
            print "continue..."
            continue
        except BaseException, e:    # 遇到新异常打印日志并退出
            print "NEW ERROR: ", e
        finally:
            edate = datetime.now()
            print "\n\n\n"
            write_index(test.sub)
            quit()
