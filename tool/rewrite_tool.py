#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author zhangxiang04@baidu.com
# @date 2013/12/12

import sys
sys.path.insert(0, '../bin')
from rp.al.utils.titlerewrite import TitleRewrite


SEP = '-'*50

def main(conf_file, in_file, out_file):
    fout = None
    try:
        tool = TitleRewrite(conf_file)
        fout = open(out_file, 'w')
        for line in open(in_file):
            line = line[:-1]    # remove enter 
            new_line = tool.rewrite_title(line, {"encoding":"utf-8,gbk,gb2312,gb18030"})
            #new_line = tool.rewrite_title(line)
            # avoid messy code
            line = line.decode('utf-8').encode('gbk') 
            out_str = '%s\n%s\n%s\n\n' % (line, new_line, SEP)
            fout.write(out_str)
    except Exception, ex:
        print '[EXP] %s' %(ex)
    finally:
        if fout:
            fout.close()
                    

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: %s conf_file raw_title_file rewrite_title_file' % sys.argv[0]
    else:
        conf_file = sys.argv[1]
        in_file = sys.argv[2]
        out_file = sys.argv[3]
        main(conf_file, in_file, out_file)
        print 'done.'
