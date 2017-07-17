#!/usr/bin/env python
# -*- coding: gbk -*-
import sys
from bin.titlerewrite import TitleRewrite

conf_file = 'conf/config.xml'
log_conf_file = 'conf/logging.conf'
tool = TitleRewrite(conf_file, log_conf_file)

params = {'encoding':'gbk'}
for line in sys.stdin:
    line_t = line.strip().split("\t")
    raw_title = line_t[0]
    new_line = tool.rewrite_title(raw_title, params)
    print raw_title, new_line
