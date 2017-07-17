#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author zhangxiang04@baidu.com
# @date 2013/12/09

import os, sys
import xml.etree.ElementTree as ET
import unicodeutil as UU

'''
基本功能
解析XML配置，返回一个配置对象
'''


def parse_config(conf_file):
    '''
    @return 失败返回None，成功返回XmlConfig对象
    '''
    try:
        config = XmlConfig()
        tree = ET.parse(conf_file)
        root = tree.getroot()
        for child in root:
            if child.tag == 'chars':
                for ele in child:
                    if ele.tag == 'begin':
                        config.chars_begin = ele.text
                    elif ele.tag == 'end':
                        config.chars_end = ele.text
                    elif ele.tag == 'anywhere':
                        config.chars_anywhere = ele.text
            elif child.tag == 'brackets':
                for ele in child:
                    tmp = {}
                    for ele2 in ele:
                        if ele2.tag == 'text':
                            tmp['text'] = ele2.text
                        elif ele2.tag == 'pos':
                            tmp['pos'] = ele2.text
                        elif ele2.tag == 'reg':    
                            tmp['reg'] = ele2.text
                        elif ele2.tag == 'file':
                            tmp['file'] = os.path.join(os.path.dirname(conf_file) , ele2.text)
                    config.brackets.append(tmp)                                                   
            elif child.tag == 'element':
                config.element = child.text
            elif child.tag == 'repetition':
                for ele in child:
                    if ele.tag == 'len':
                        if ele.text.find(',') != -1:
                            region = ele.text.split(',')
                            config.rep_len = (int(region[0]), int(region[1]))
                        else:
                            config.rep_len = (int(ele.text), sys.maxint)
                    elif ele.tag == 'times':
                        if ele.text.find(',') != -1:
                            region = ele.text.split(',')
                            config.rep_times = (int(region[0]), int(region[1]))
                        else:
                            config.rep_times = (int(ele.text), sys.maxint)
                    elif ele.tag == 'action':
                        config.rep_action = ele.text
            elif child.tag == 'replaces':
                for ele in child:
                    tmp = {}
                    for ele2 in ele:
                        if ele2.tag == 'from':
                            tmp['from'] = ele2.text
                        elif ele2.tag == 'to':
                            tmp['to'] = ele2.text
                    config.replaces.append(tmp)
            elif child.tag == 'outputencoding':
                config.output_encoding = child.text
    except Exception, ex:
        print 'exception:%s' %ex
        config = None
    return config

   


class XmlConfig:

    def __init__(self):
        '''
        配置需要过滤的字符以及该字符出现的位置
        每个元素为一个字符
        '''
        self.chars_begin = []
        self.chars_end = []
        self.chars_anywhere = []

        '''
        配置需要过滤的括号、位置、匹配的内容
        每个brackets元素为一个字典，包含以下kv对
        text：括号类型，多个用逗号分隔
        pos：括号位置（begin/end/anywhere）
        reg/file：括号内文本内容模式串或模式文件
        '''
        self.brackets = []

        # 配置保留的文本成分（中文ch、英文en、数字digit、其他else）
        self.element = []

        # 配置重复文本长度、次数、处理方式（remove/reservefirst/reservelast）
        self.rep_len = (2, 2)
        self.rep_times = (3, 3)
        self.rep_action = 'remove'

        '''
        配置替换功能
        每个replaces元素包含以下kv对
        from：待替换的子串，多个子串逗号分隔，若子串包含逗号，需用\,来表示
        to：替换的目标子串
        '''
        self.replaces = []

        # 改写后的编码
        self.output_encoding = 'utf-8'

    def __str__(self):
        encoding = 'gbk'
        return 'chars:[%s %s %s]\nbracket:%s\nrep:[%s %s %s]\nreplaces:%s\nelement:%s\noutput_encoding:%s' % (\
                UU.codec(self.chars_begin, to_encoding=encoding), \
                UU.codec(self.chars_end, to_encoding=encoding), \
                UU.codec(self.chars_anywhere, to_encoding=encoding), \
                self.brackets, \
                self.rep_len, self.rep_times, self.rep_action, \
                self.replaces, \
                self.element, \
                self.output_encoding)


if __name__ == '__main__':
    #conf_file = './config.xml'
    conf_file = '/home/users/zhangxiang04/project/title-rewrite2/tool/config.xml'
    cfg = parse_config(conf_file)
    print cfg



