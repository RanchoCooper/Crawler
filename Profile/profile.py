#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-21 13:54
# @email    : rancho941110@gmail.com

'''got all seeds refers to Profile
features:
- unified encoding
- Lantin and non-Lantin together
- schedule bar(little format bugs)
-
other: cancle RandomAgent

todo:
- argparse
- * using threading
'''

import sys
import json
import requests
import argparse

parser = argparse.ArgumentParser(description='Fetch all urls refer to profile')


class Directory(object):
    """read directory"""
    def __init__(self, index):
        # const variable
        self.base = 'http://www.linkedin.com/directory/people-'
        self.split = '-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'
        self.limit = [26, 100]

        self.url = ''                           # seed url to parse profile refers
        self.result = []                        # save profile refers
        self.index = index

        # aka. -perple-x-x-x, but `Latin` would be -people-x-x-x-x
        # since then added `rank` circulation internally

    def traverse(self):
        """
        Lantin:    'people-init-page-line'
        no-Lantin: 'people-init-page-line-rank'
        Q: parallel them together
        """
        # self.index = load_index()
        while self.index[0] <= self.limit[0]:
            while self.index[1] <= self.limit[1]:
                # info: -init-page
                while self.index[2] <= self.limit[1]:
                    # Lantern
                    print self.split.join([chr(self.index[0] + 96), str(self.index[1]), str(self.index[2])])
                    while self.index[3] <= self.limit[1]:
                        # change init from number to alphabet
                        sub_seq = chr(self.index[0] + 96), str(self.index[1]), str(self.index[2]), str(self.index[3])
                        self.url = self.base + self.split.join(sub_seq)
                        if self.get_page(self.url):
                            self.parse(self.response)
                            self.printBar(self.index[3])
                            self.save_tofile()
                        else:
                            break
                        write_index(self.index)
                        self.index[3] += 1
                    self.index[3] = 1   # reset

                    # non-Lantern
                    print self.split.join([chr(self.index[0]), str(self.index[1])])
                    sub_seq = str(self.index[0]), str(self.index[1]), str(self.index[2])
                    self.url = self.base + self.split.join(sub_seq)
                    if self.get_page(self.url):
                        self.parse(self.response)
                        self.printBar(self.index[2])
                        self.save_tofile()
                    else:
                        break
                    self.index[2] += 1
                self.index[2] = 1       # reset
                self.index[1] += 1
            self.index[1] = 1           # reset
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
    with open('index.json', 'w') as f:
        json.dump(data, f)

def load_index():
    """return the list of 4 element loaded from index.json"""
    re = []
    with open('index.json', 'r') as f:
        data = json.load(f)
    for item in data:
        re.append(item)
    return re

if __name__ == '__main__':
    last = load_index()
    print "recover from ", last
    test = Directory(last)
    test.traverse()
    pass
