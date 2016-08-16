#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-29 10:11
# @email    : rancho941110@gmail.com

'''获取所有注册用户的主页链接
features:
- 08.10优化日志信息
- 08.08生成器代替while循环
其他: 去掉了随机agent(测试发现直接发包没问题)

- 08.16多线程模型
'''

import sys
import requests
import json
from lxml import etree
from Queue import Queue
from threading import Thread
from time import clock, sleep
from datetime import datetime
from itertools import dropwhile

count = 0

WORK_QUEUE_SIZE = 100

sys.stderr = open('wrong', 'a+')

class Downloader():
    def __init__(self):
        self.split = '-'
        self.base = 'http://www.linkedin.com/directory/people-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'

    # target for Thread, need sub as args
    def fetch(self):
        global q, count
        while True:
            if q.empty():
                sleep(0.1)
            if not q.empty():
                url = self.base + self.split.join(q.get())
                try:
                    res = requests.get(url)
                    if res.status_code == 200:
                        with open('all', 'a+') as f:
                            for refer in self.parse_page(res):
                                if isinstance(refer, str):
                                    f.write(refer)
                                elif isinstance(refer, unicode):
                                    f.write(refer.encode('utf8'))
                                else:
                                    sys.stderr.write('[Unknow encode]: @', url)
                                    continue
                            print "saved ", url
                            count += 1
                except requests.ConnectionError:
                    sys.stderr.write('[Requests failed]: %s' % url)

    def parse_page(self, text):
        selector = etree.HTML(text.content)
        return selector.xpath(self.pattern)

class Travelor(object):
    def __init__(self, index):
        self.prog = 0               # flag for progress

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
        p = (1 - s / c) * 100
        print "START at %32s"               % sdate
        print "ENDED at %32s"               % edate
        print "RUN time used: %26.3f"       % s
        print "CPU time used: %26.3f"       % c
        print "IO  time used: %25.3f%%"     % p
        if count:
            petime = count / s
            print "Requests page: %26d"     % count
            print "Average  rate: %24.3f/s" % petime
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

    for i in range(WORK_QUEUE_SIZE):
        workers.append(Thread(target=download.fetch))

    try:
        for work in workers:
            work.daemon = True
            work.start()

        for refer in traverse.traverse():
            while True:
                if q.full():
                    continue
                else:
                    q.put(refer)
                    break

    finally:
            edate = datetime.now()
            print "\n\n\n"
            quitter()
