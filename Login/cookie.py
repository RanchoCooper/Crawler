#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-19 15:02
# @email    : rancho941110@gmail.com

import urllib2
import cookielib

class Cookie(object):
    """
    Handle with cookie
    """
    def __init__(self, url, filename=None):
        if filename:
            self.cookie = cookielib.MozillaCookieJar(filename)
        else:
            self.cookie = cookielib.CookieJar()
        self.handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.handler)
        self.response = self.opener.open(url)
        self.cookie.save(ignore_discard=True, ignore_expires=True)

    def printCookie(self):
        for item in self.cookie:
            print 'Name = ' + item.name
            print 'Value = ' + item.value

if __name__ == '__main__':
    url = 'https://www.linkedin.com/'
    fname = 'cookie.txt'
    test = Cookie(url, fname)
    test.printCookie()
