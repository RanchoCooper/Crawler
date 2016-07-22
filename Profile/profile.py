#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-21 13:54
# @email    : rancho941110@gmail.com

'''got all url refer to profile'''

# from bs4 import BeautifulSoup
import sys
import random
import requests

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
    def __init__(self, base):
        self.base = base
        self.split = '-'
        self.result = []

    def traverse(self):
        capital = 1
        while capital <= 26:
            page = 1
            while page <= 100:
                index = 1
                print "located at %d-%d" % (capital, page)

                while index <= 100:
                    sub_seq = str(capital), str(page), str(index)   # alse as filename
                    url = self.base + self.split.join(sub_seq)

                    self.printBar(index)
                    # get directory page
                    head = {}
                    head['User-Agent'] = RandomAgent().get()

                    response = requests.get(url, headers=head)
                    if response.status_code == 200:
                        self.parse(response.content)
                        self.save_tofile(str(capital))
                    elif response.status_code == '404':
                        continue
                    else:
                        # write to log
                        pass

                    index += 1
                    print
                page += 1
            capital += 1

    def save_tofile(self, fnm):

        f = open(fnm, 'a+')
        for item in self.result:
            if not isinstance(item, unicode):
                f.write(item)
                f.write('\n')
        f.close()

    def parse(self, text):
        from lxml import etree
        selector = etree.HTML(text)
        self.result = selector.xpath('//*[@id="seo-dir"]/div/div[5]/div/ul//a/@href')

    def printBar(self, index):
        percent = index / 5
        bar_str = '[' + '#' * percent + ' ' * (20 - percent) + ']' + '\r'

        sys.stdout.write(str(index))
        sys.stdout.write(bar_str)
        sys.stdout.flush()

if __name__ == '__main__':
    base = "http://www.linkedin.com/directory/people-"
    test = Directory(base)
    test.traverse()

    # detect uppper limit
