#!/usr/bin/env python
#! -*-coding:utf-8 -*-
# @author zhangxiang04@baidu.com
# @date 2013/12/11

import unittest
import sys
sys.path.insert(0, '../bin')
import time
import rp.al.utils.chardet as chardet


class ChardetTestCase(unittest.TestCase):  

    def test_detect(self):
        '''
        detect text encoding
        '''
        # 原始编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        # 希望检测出的编码
        expected = ['utf-8', 'gb2312', 'gb2312', 'gb2312']
        for idx, encoding in enumerate(encodings):
            a_str = u'这是一个测试www.test.cn'.encode(encoding)
            detect_encoding = chardet.detect(a_str)['encoding']
            self.assertEquals(expected[idx].lower(), detect_encoding.lower())


