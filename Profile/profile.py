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
import requests
from time import clock
from timeit import default_timer
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
        for sub in dropwhile(lambda sub: sub != history, gen):
            self.sub = sub
            write_index(sub)
            # sleep(0.01)
            if len(sub) == 4:
                sub = list(sub)
                sub[0] = chr(sub[0] + 96)

            # GET PAGE
            current = sub[-1]
            self.url = self.base + self.split.join(list(map(lambda x: str(x), sub)))
            print self.url
            # push to work queue
            if self.get_page(self.url):
                # 得到相应页面后的操作, 解析出主页链接并保存
                self.count += 1         # 统计发包数(不计404)
                self.parse(self.response)
                self.printBar(current)
                self.save_tofile()

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
        with open('1', 'a+') as f:
            for item in self.result:
                if isinstance(item, str):
                    f.write(item)
                elif isinstance(item, unicode):
                    f.write(item.encode('utf8'))
                else:
                    f.write('@@@@@@@@@\n\n\n')
                    f.write(item)
                f.write('\n')

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
        c = clock()
        r = default_timer() - start
        iotime = (1 - c / r) * 100
        print "CPU time used: %20.3f"     % c
        print "PRO time used: %20.3f "    % r
        print "IO  time used: %20.3f %%"  % iotime
        if test.count:
            petime = test.count / r
            print "Requests page: %20d"       % test.count
            print "Average %20.5f Page per sec" % petime
        print
        print "exit, see you..."
        return func()
    return wrapper

@timelogging
def quit():
    sys.exit()

if __name__ == '__main__':
    start = default_timer()
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
            write_index(test.sub)
            current = load_index()
            quit()
