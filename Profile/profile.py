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
其他: 去掉了随机agent(测试发现直接发包没问题)

todo:
- * 多线程模型
'''

import sys
import json
import Queue
import requests
import threading
from time import clock, time

_WORK_THREAD_NUM = 5        # 设置线程个数
_MAX_QUEUE_SIZE  = 20       # 设置队列大小

class WorkQueue(object):
    """为获取页面提供一个先入先出的工作队列"""
    def __init__(self, size):
        self.size = size
        self.queue = Queue.Queue(maxsize=size)
        self.flag = False   # 队满标志

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
        Directory.count = 0
        self.base = 'http://www.linkedin.com/directory/people-'
        self.split = '-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'
        self.limit = [26, 100]

        self.url = ''                           # 发请求包时的url
        self.result = []                        # 页面解析后含有refer的列表
        self.index = index

        self.generator = ([i, p, l, r]
                            for i in xrange(1, 27)
                            for p in xrange(1, 101)
                            for l in xrange(1, 101)
                            for r in xrange(1, 101))

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

    def traverse(self):
        """
        数字和字母的url 分别为 -perple-数字-x-x 和 -people-字母-x-x-x
        前者三层, 后者有四层, 所以在三层循环框架里加了一层来跑字母
        字母rank部分遍历完后再就继续遍历数字
        从发包角度来说, 每请求100页字母目录, 然后请求一页数字目录

        数字开头:    'people-数字-page-line'
        字母开头:    'people-字母-page-line-rank'

        瓶颈: 开线程池做到并行化
        """

        while self.index[0] <= self.limit[0]:
            while self.index[1] <= self.limit[1]:
                while self.index[2] <= self.limit[1]:
                    # 当前进度
                    print self.split.join([chr(self.index[0] + 96), str(self.index[1]), str(self.index[2])])
                    # 百页字母
                    while self.index[3] <= self.limit[1]:
                        # 数字转字母, 并获取发包所需的url
                        sub_seq = chr(self.index[0] + 96), str(self.index[1]), str(self.index[2]), str(self.index[3])
                        self.url = self.base + self.split.join(sub_seq)
                        if self.get_page(self.url):
                            # 得到相应页面后的操作, 解析出主页链接并保存
                            self.parse(self.response)
                            self.printBar(self.index[3])
                            self.save_tofile()
                            Directory.count += 1
                        else:
                            break
                        write_index(self.index)
                        self.index[3] += 1
                    self.index[3] = 1

                    # 一页数字
                    print self.split.join([str(self.index[0]), str(self.index[1]), str(self.index[2])])
                    sub_seq = str(self.index[0]), str(self.index[1]), str(self.index[2])
                    self.url = self.base + self.split.join(sub_seq)
                    if self.get_page(self.url):
                        # 得到相应页面后的操作, 解析出主页链接并保存
                        self.parse(self.response)
                        self.save_tofile()
                        Directory.count += 1
                    else:
                        break
                    self.index[2] += 1
                self.index[2] = 1
                self.index[1] += 1
            self.index[1] = 1
            self.index[0] += 1

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

    def printBar(self, index):
        percent = index / 5
        bar_str = '[' + '#' * percent + ' ' * (20 - percent) + ']' + '\r'

        sys.stdout.write(str(index))
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
        print "page had GET : %10d" % Directory.count
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
            test.traverse()
            # test.testing()
        except requests.exceptions.ConnectionError, e:
            print "\n\nWRONG: %s" % e
            print "continue..."
            continue
        except KeyboardInterrupt:
            print "\n\n\n"
            current = load_index()
            quit()