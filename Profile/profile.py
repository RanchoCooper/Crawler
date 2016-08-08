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

- 08.08生成器代替while循环
其他: 去掉了随机agent(测试发现直接发包没问题)

todo:
- * 多线程模型
'''

import sys
import json
import Queue
import requests
# import threading
from time import clock, time
from itertools import dropwhile

_WORK_THREAD_NUM = 5        # 设置线程个数
_MAX_QUEUE_SIZE  = 20       # 设置队列大小

class WorkQueue(object):
    """为获取页面提供一个先入先出的工作队列"""
    def __init__(self, size):
        self.size = size
        self.flag = False   # 队满标志
        self.queue = Queue.Queue(maxsize=size)

class Schedule(object):
    """调度器, 控制线程的执行"""
    def __init__(self, size):
        self.full = False       # 满标志
        self.empty = False      # 空标志
        self.current = 0        # 当前执行数
        self._MAX    = 5        # 最大执行数
        pass

    def work(self, func, *args):
        """任务执行"""
        pass

class Directory(object):
    """遍历目录"""
    def __init__(self, index):
        # 一些常量
        self.base = 'http://www.linkedin.com/directory/people-'
        self.split = '-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'
        self.count = 0
        self.theriry_total = 26260000
        self.alphabet = [i for i in range(1, 27)]
        self.numrange = [i for i in range(1, 101)]

        # share lock!
        self.url = ''                           # 发请求包时的url
        self.result = []                        # 页面解析后含有refer的列表
        self.index = index

    # 用生成器代替原有的while循环
    # 新特性: 代理迭代, 迭代目录与发包请求异步进行
    # 不变特性: 自动恢复(迭代跃进), 终止检测(需要bool flag配合来完成)
    def generator(self):
        for init in self.alphabet:
            for page in self.numrange:
                for line in self.numrange:
                    for rank in self.numrange:
                        lan_item = init, page, line, rank
                        yield lan_item
                    non_item = init, page, line
                    yield non_item

    def start_traverse(self):
        history = tuple(self.index)
        gen = self.generator()
        for item in dropwhile(lambda item: item != history, gen):
            write_index(item)
            if len(item) == 4:
                item = chr(item[0] + 96), item[1], item[2], item[3]

            # GET PAGE
            current = item[-1]
            self.url = self.base + self.split.join(list(map(lambda x: str(x), item)))

            # push to work queue

            if self.get_page(self.url):
                # 得到相应页面后的操作, 解析出主页链接并保存
                self.count += 1         # 统计发包数(不计404)
                self.parse(self.response)
                self.printBar(current)
                self.save_tofile()

    def workding(self, sub):
        """线程执行的target"""
        url = self.base + sub       # change
        print "fetch url: ", url
        pass

    def prepare(self):
        while True:
            g = list(self.generator.next())
            print "current g", g
            if g == self.index:
                break
        print "now next is ", self.generator.next()

    def get_page(self, url):
        self.response = requests.get(self.url)
        if self.response.status_code == 200:
            return True
        elif self.response.status_code == '404':
            return None
        else:
            # write to log
            return True

    def parse(self, text):
        from lxml import etree
        selector = etree.HTML(text.content)
        self.result = selector.xpath(self.pattern)

    def save_tofile(self):
        f = open('1', 'a+')
        for item in self.result:
            if isinstance(item, str):
                f.write(item)
            elif isinstance(item, unicode):
                f.write(item.encode('utf8'))
            else:
                f.write('@@@@@@@@@\n\n\n')
                f.write(item)
            f.write('\n')
        f.close()

    def printBar(self, current):
        percent = current / 5
        bar_str = '[' + '#' * percent + ' ' * (20 - percent) + ']' + '\r'

        sys.stdout.write(str(current))
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
        print "CPU time used: %10.5f" % clock()
        print "running time : %10.5f " % (time() - start)
        print "page had GET : %10d" % test.count
        return func()
    return wrapper

@timelogging
def quit():
    sys.exit()

if __name__ == '__main__':
    start = time()
    while True:

        try:
            origin = load_index()   # 从json读历史记录, 要指定起始位置可以直接改json
            print "recover from ", origin
            test = Directory(origin)
            test.start_traverse()
        except requests.exceptions.ConnectionError, e:
            print "\n\nWRONG: %s" % e
            print "continue..."
            continue
        except KeyboardInterrupt:
            print "\n\n\n"
            current = load_index()
            quit()
