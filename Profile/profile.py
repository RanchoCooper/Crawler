#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-29 10:11
# @email    : rancho941110@gmail.com

'''
获取所有注册用户的主页链接
features:
- 08.08生成器代替while循环
- 08.10优化日志信息
- 08.16多线程模型
其他:
不支持自动续爬
不确定最佳的线程数
异常日志保存在wrong文件里

Bug:
- 等待所有线程终止无法捕获键盘中断
'''

import sys
import json
import requests
from lxml import etree
from Queue import Queue
from time import sleep
from threading import Thread
from datetime import datetime
from itertools import dropwhile

count = 0       # 统计发包数
users = 0       # 统计用户数

WORK_QUEUE_SIZE = 100       # 工作队列和线程池大小

sys.stderr = open('wrong', 'a+')

class Travelor(object):
    def __init__(self, index):
        self.history = index
        self.alphabet = [i for i in range(1, 27)]
        self.numrange = [i for i in range(1, 101)]

    def generator(self):
        for init in self.alphabet:
            for page in self.numrange:
                for line in self.numrange:
                    non_sub = [init, page, line]
                    yield non_sub
                    for rank in self.numrange:
                        lan_sub = [init, page, line, rank]
                        yield lan_sub

    def traverse(self):
        gen = self.generator()
        for sub in dropwhile(lambda index: index != self.history, gen):
            if len(sub) == 4:
                sub[0] = chr(sub[0] + 96)
            yield map(lambda x: str(x), sub)

class Downloader():
    def __init__(self):
        self.split = '-'
        self.base = 'http://www.linkedin.com/directory/people-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'

    def fetch(self):
        global q, count, users
        while True:
            if q.empty():
                sleep(0.1)
            if not q.empty():
                url = self.base + self.split.join(q.get())
                try:
                    res = requests.get(url)
                    if res.status_code == 200:
                        # 打开IO接口
                        with open('all', 'a+') as f:
                            for refer in self.parse_page(res):
                                if isinstance(refer, str):
                                    f.write(refer)
                                    users += 1
                                elif isinstance(refer, unicode):
                                    f.write(refer.encode('utf8'))
                                    users += 1
                                else:
                                    sys.stderr.write('[Unknow encode]: %s\n', url)
                                    continue
                                f.write('\n')
                            print "saved ", url
                            count += 1
                except requests.ConnectionError:
                    sys.stderr.write('[Requests failed]: %s\n' % url)
                except BaseException, e:
                    sys.stderr.write('[Unknow Error]: %s\n' % e)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt

    def parse_page(self, text):
        selector = etree.HTML(text.content)
        return selector.xpath(self.pattern)

def load_index():
    """从json导入开始位置"""
    re = []
    with open('index.json', 'r') as f:
        data = json.load(f)
    for item in data:
        re.append(item)
    return re

def timelogging(func):
    def wrapper():
        s = (edate - sdate).total_seconds()
        print "START at %32s"               % sdate
        print "ENDED at %32s"               % edate
        print "RUN time used: %26.3f"       % s
        if count:
            ppage = count / s
            print "Average  rate: %26.3f/s" % ppage
            print "Requests page: %26d"     % count
            print "Fetched users: %26d"     % users
        print
        print "exit, see you..."
        return func()
    return wrapper

@timelogging
def quitter():
    sys.exit()

if __name__ == '__main__':
    sdate = edate = datetime.now()

    origin = load_index()
    print "start at ", origin

    download = Downloader()
    traverse = Travelor(origin)

    workers = []
    q = Queue(WORK_QUEUE_SIZE)

    # 准备工作队列
    for i in range(WORK_QUEUE_SIZE):
        workers.append(Thread(target=download.fetch))

    try:
        # 启动工作队列
        for work in workers:
            work.daemon = True
            work.start()

        # 迭代目录生成器
        for refer in traverse.traverse():
            while True:
                if q.full():
                    continue
                else:
                    q.put(refer)
                    break
    finally:
        # 等待所有线程终止
        # for work in workers:
        #     work.join()
        edate = datetime.now()
        print "\n\n\n"
        quitter()
