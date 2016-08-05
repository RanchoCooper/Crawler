#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author   : Rancho Cooper
# @date     : 2016-07-18 14:53
# @email    : rancho941110@gmail.com

from ctypes import c_uint32, sizeof

class BitMap(object):
    """
    BitMap is a efficient datastructure for mass data
    easy to uniquify each other between two items

    later comes with C version for better speed!
    if it's necessary
    """
    def __init__(self, max):
        self.leng = sizeof(c_uint32) << 3           # length of each element(Bits)
        self.size = self.ElemIndex(max, True)      # maximum index of bitmap
        self.table = [0 for i in range(self.size)]

    def ElemIndex(self, num, up=False):
        return num / self.leng + (1 if up else 0)

    def BitIndex(self, num):
        return num % self.leng

    def setBit(self, num):
        elemNo = self.ElemIndex(num)
        bitsNo = self.BitIndex(num)
        self.table[elemNo] |= (1 << bitsNo)

    def clearBit(self, num):
        elemNo = self.ElemIndex(num)
        bitsNo = self.BitIndex(num)
        self.table[elemNo] &= ~(1 << bitsNo)

    def testBit(self, num):
        elemNo = self.ElemIndex(num)
        bitsNo = self.BitIndex(num)
        return True if (self.table[elemNo] & (1 << bitsNo)) else False

if __name__ == '__main__':
    bitmap = BitMap(256)
    test = 16
    sz = bitmap.size
    print '%d elements needed' % sz
    print '%d should belong to %d element' % (test, bitmap.ElemIndex(test))
    print '%d should belong to %d element and the %d bit' % (test, bitmap.ElemIndex(test), bitmap.BitIndex(test))

    bitmap.setBit(4)
    print bitmap.table
