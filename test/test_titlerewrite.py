#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @author zhangxiang04@baidu.com
# @date 2013/12/10

import sys
sys.path.insert(0, '../bin')
import unittest
from rp.al.utils.titlerewrite import TitleRewrite

class TitleRewriteTestCase(unittest.TestCase):

    CONF_FILE = 'test_config.xml'
    LOG_CONF_FILE = 'logging.conf'

    def setUp(self):
        self.tool = TitleRewrite(TitleRewriteTestCase.CONF_FILE, \
                TitleRewriteTestCase.LOG_CONF_FILE)

    def tearDown(self):
        pass

    def assertTupleEquals(self, tup1, tup2):
        self.assertEquals(len(tup1), len(tup2))
        for idx in range(0, len(tup1)):
            self.assertTrue(tup1[idx] == tup2[idx])

    def test_find_all_brackets(self):
        a_str = u'[test]aaa(test2)bbb{test3}【测试】end.'
        bracket_info = self.tool.find_all_brackets(a_str)
        self.assertTrue(bracket_info)
        self.assertEquals(4, len(bracket_info))
        self.assertTupleEquals(bracket_info[0], (1, u'[]', 0, 5))
        self.assertTupleEquals(bracket_info[1], (2, u'()', 9, 15))
        self.assertTupleEquals(bracket_info[2], (3, u'{}', 19, 25))
        self.assertTupleEquals(bracket_info[3], (4, u'\u3010\u3011', 26, 29))

    def test_filter_chars(self):
        a_str = '!!~this*** is# a test.+++++--++'
        new_str = self.tool.filter_chars(a_str)
        self.assertEquals('this is a test.', new_str)
        a_str = '** ~!this ##is!! a +++--++test.+!**-'
        new_str = self.tool.filter_chars(a_str)
        self.assertEquals(' ~!this is!! a +++--++test.+!', new_str)
        #print new_str
    
    def test_filter_brackets(self):
        # 删除任意位置的()[]{}，且任意内容的括号
        a_str = '[test]aaa(test2)bbb{test3}ccc'
        new_str = self.tool.filter_brackets(a_str)
        self.assertEquals('aaabbbccc', new_str)
        # 仅删除开头/结尾的【】，且内容包含www/http
        a_str = u'【测试www.test.cn】[test]aaa【测试http】(test2)bbb{test3}ccc【测试http://?】'
        new_str = self.tool.filter_brackets(a_str)
        self.assertEquals(u'aaa【测试http】bbbccc', new_str)
        #print new_str

    
    def test_filter_repeated_substr(self):
        a_str = u'测试标题www.测试这是一个标题'
        new_str = self.tool.filter_repeated_substr(a_str)
        #print new_str
        self.assertEquals(u'www.这是一个', new_str)
        a_str = u'1xxoo,xxoo,xxoo电影,xxoo小说,xxoo图片,xxoo网站,你懂的网站,...'
        new_str = self.tool.filter_repeated_substr(a_str)
        self.assertEquals(u'1电影小说图片你懂的...', new_str)
        #print new_str

    def test_replace_substr(self):
        a_str = u'+++试标--题www|测试|这是一个|标题+-*/'
        a_str = self.tool.replace_substr(a_str)
        self.assertEquals(u'---试标--题www。测试。这是一个。标题--*/', a_str)
        a_str = u'|测试|标题www|测试|这是一个|标题+-*|'
        a_str = self.tool.replace_substr(a_str)
        self.assertEquals(u'。测试。标题www。测试。这是一个。标题--*。', a_str)
        #print a_str

    def test_unicode_encode(self):
        a_str = u'测试，这是一个测试样本。'
        encoding = 'gbk'
        a_gbk_str = self.tool.unicode_encode(a_str, encoding)
        try:
            a_gbk_str.decode(encoding)
        except Exception,ex:
            self.fail('encoding incorrect:%s' %ex)
        #print a_gbk_str
    
    def test_extract_element(self):
        a_str = u'##这是一个测试www测试.baidu.com123test**'
        a_str = self.tool.extract_element(a_str, ['digit', 'ascii'])
        self.assertEquals(u'##..123**', a_str)
        a_str = u'##这是一个测试www测试.baidu.com123test**'
        a_str = self.tool.extract_element(a_str, ['ch', 'en'])
        self.assertEquals(u'这是一个测试www测试baiducomtest', a_str)
        #print a_str

    def test_decode_to_unicode(self):
        # 指定编码        
        a_utf8_str = u'这是一个测试test.'.encode('utf-8')
        a_unicode_str = self.tool.decode_to_unicode(a_utf8_str, 'utf-8')
        self.assertTrue(isinstance(a_unicode_str, unicode))
        a_gbk_str = u'另外一个测试test.'.encode('gbk')
        a_unicode_str = self.tool.decode_to_unicode(a_gbk_str, 'gbk')
        self.assertTrue(isinstance(a_unicode_str, unicode))
        # 不指定编码
        a_utf8_str = u'这是一个测试test.'.encode('utf-8')
        a_unicode_str = self.tool.decode_to_unicode(a_utf8_str)
        self.assertTrue(isinstance(a_unicode_str, unicode))
        a_gbk_str = u'另外一个测试test.'.encode('gbk')
        a_unicode_str = self.tool.decode_to_unicode(a_gbk_str)
        self.assertTrue(isinstance(a_unicode_str, unicode))
        #print a_unicode_str
    
    def test_check_encode(self):
        a_utf8_str = u'这是一个测试test.'.encode('utf-8')
        self.assertEquals('utf-8', self.tool.check_encode(a_utf8_str, ['utf-8', 'gbk2312', 'gbk', 'gb18030']))

        a_gb2312_str = u'另外一个测试test.'.encode('gb2312')
        self.assertEquals('gb2312', self.tool.check_encode(a_gb2312_str, ['utf-8', 'gb2312', 'gbk', 'gb18030']))

        a_gbk_str = u'另外一个测试test.'.encode('gbk')
        self.assertEquals('gb2312', self.tool.check_encode(a_gbk_str, ['utf-8', 'gb2312', 'gbk', 'gb18030']))

        a_gb18030_str = u'另外一个测试test.'.encode('gb18030')
        self.assertEquals('gb2312', self.tool.check_encode(a_gb18030_str, ['utf-8', 'gb2312', 'gbk', 'gb18030']))

        a_unicode_str = u'另外一个测试test.'
        self.assertEquals('unicode', self.tool.check_encode(a_unicode_str, ['utf-8', 'gb2312', 'gbk', 'gb18030']))


    def test_rewrite_title(self):
        a_str = u'[海盗美剧.hdmeiju.com]超人：钢铁之躯.man.of.steel.2013.720p.bluray.x264.bcehd-hdmeiju'
        new_str = self.tool.rewrite_title(a_str)
        self.assertEquals(u'超人：钢铁之躯.man.of.steel.13.7pluray.x264ce-meiju'.encode('gbk'), new_str)
        #print new_str








