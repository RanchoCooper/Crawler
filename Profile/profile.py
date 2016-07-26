#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-21 13:54
# @email    : rancho941110@gmail.com

'''got all seeds refers to Profile

features:
- unified encoding
- Lantin and non-Lantin
- schedule bar
-

todo:
- /pub/dir          change pattern
-
'''

# from bs4 import BeautifulSoup
import sys
import random
import requests

base = "http://www.linkedin.com/directory/people-"

class RandomAgent(object):
    def __init__(self):
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

    def get(self):
        self.useragent = random.choice(self.user_agent_list)
        return self.useragent

class Directory(object):
    """read directory"""
    def __init__(self, base, init=1, page=1, line=1, rank=1):
        # const variable
        self.base = base
        self.split = '-'
        self.pattern = '//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href'
        self.scan_limit = [26, 100]

        self.url = ''                           # seed url to parse profile refers
        self.head = {}                          # user-agent
        self.result = []                        # save profile refers
        self.index = [init, page, line, rank]

        # aka. -perple-x-x-x, but `Latin` would be -people-x-x-x-x
        # since then added `rank` circulation internally

    def traverse(self):
        """
        Lantin:    'people-init-page-line'
        no-Lantin: 'people-init-page-line-rank'
        Q: parallel them together
        """
        while self.index[0] <= self.scan_limit[0]:
            while self.index[1] <= self.scan_limit[1]:
                # info: -init-page
                print "located at %d-%d" % (self.index[0], self.index[1])
                while self.index[2] <= self.scan_limit[1]:
                    # get_page detect continue or break

                    # Lantern
                    while self.index[3] <= self.scan_limit[1]:
                        # change init from number to alphabet
                        sub_seq = chr(self.index[0] + 96), str(self.index[1]), str(self.index[2]), str(self.index[3])
                        self.url = self.base + self.split.join(sub_seq)
                        if self.get_page(self.url):
                            self.parse(self.response)
                            self.printBar(self.index[3])
                            self.save_tofile()
                        else:
                            break
                        self.index[3] += 1
                    self.index[3] = 1   # reset

                    # non-Lantern
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
        self.head['User-Agent'] = RandomAgent().get()
        self.response = requests.get(self.url, headers=self.head)
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
            if isinstance(item, basestring):
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

if __name__ == '__main__':
    test = Directory(base)
    test.traverse()
