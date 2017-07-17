#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import time
import xmlconfig
import re
import chardet
import logging
import logging.config
import suffixarray as sa
import unicodeutil as uu

PWD = os.path.split(os.path.realpath(__file__))[0]


class TitleRewrite(object):
    '''
    网页Title改写模块，支持以下改写功能：
    1.删除指定位置（begin/end/anywhere）的指定字符
    2.删除指定位置的指定类型的括号（若括号内的文本匹配指定模式）
    3.保留特定的文本成分（中文、英文、数字、ASCII、其他）
    4.重复子串的检测，以及三种处理方式（remove/reservefirst/reservelast）
    5.子串替换
    6.文本编码的自动检测与转换
    '''

    def __init__(self, conf_file, log_conf_file=None):
        if not os.path.exists(conf_file):
            raise Exception, 'conf_file "%s" does not exists.' % conf_file
        if not log_conf_file:
            self.log = None
        elif not os.path.exists(log_conf_file):
            raise Exception, 'log_conf_file "%s" does not exists.' % log_conf_file
        else:
            logging.config.fileConfig(log_conf_file)
            self.log = logging.getLogger("titlerewrite")

        # init config 
        self.cfg_file = conf_file
        self.cfg = xmlconfig.parse_config(conf_file)
        if not self.cfg:
            raise Exception, 'Fail to parse conf_file.'
        # 将bracket配置中的reg表达式进行编译，并转化为map
        self.brackets = self.handle_brackets_config(self.cfg)


    def rewrite_title(self, raw_title, params=None):
        '''
        @param raw_title 原始的title
        @param params 额外的参数
        @return 失败返回None，成功返回改写后的title
        '''
        s_time = time.time()
        try:
            # params参数解析，编码检测
            encoding = None # raw_title的编码
            detect_flag = True   # 是否自动检测编码
            if params and 'encoding' in params and params['encoding']:
                encs = params['encoding'].strip().split(',')
                # 指定了有效的候选编码列表
                if encs:
                    encoding = self.check_encode(raw_title, encs)
                    if encoding:
                        detect_flag = False
                    else:
                        raise Exception, 'The sepcified encoding list is invalid.'
            
            # 统一转化为Unicode
            a_str = self.decode_to_unicode(raw_title, encoding, detect_flag)
            if not a_str:
                raise Exception, 'decode_to_unicode error.'

            # 过滤字符
            a_str = self.filter_chars(a_str)
    
            # 过滤括号
            a_str = self.filter_brackets(a_str)

            # 过滤重复文本
            a_str = self.filter_repeated_substr(a_str)

            # 筛选文本成分
            a_str = self.extract_element(a_str, self.cfg.element)

            # 替换子串
            a_str = self.replace_substr(a_str)

            # TODO增加子串

            # 编码转换
            a_str = self.unicode_encode(a_str, self.cfg.output_encoding)

            return a_str
        except Exception, ex:
            if not self.log:
                sys.stderr.write('[EXP] %s\n' %ex)
            else:                
                self.log.error('Rewrite exception:%s' %ex)
        return None

    def check_encode(self, a_str, encodings):
        '''
        从用户指定的encodings列表中找出a_str的编码

        @return 失败返回None, 成功返回a_str的编码
        '''
        if isinstance(a_str, unicode):
            return 'unicode'
        res = None
        for enc in encodings:
            try:
                if a_str == a_str.decode(enc).encode(enc):
                    res = enc
                    break
            except Exception, ex:
                pass
        return res


    def decode_to_unicode(self, a_str, encoding=None, detect=True):
        '''
        将一个任意编码类型的字符串转为unicode字符串

        @param encoding 指定a_str的编码
        @param detect 若encoding=None，是否检测编码
        @return 若无法检测编码，返回None；否则返回unicode字符串 
        '''
        if isinstance(a_str, unicode):
            return a_str
        try:
            en = encoding
            if not en and detect:
                char_info = chardet.detect(a_str)
                if char_info:
                    en = char_info['encoding']
            # 不指定编码，也无法检测出编码
            if not en:
                return None
            return a_str.decode(en)
        except Exception, ex:
            if not self.log:
                sys.stderr.write('[EXP] %s\n' %ex)
            else:                
                self.log.error('decode_to_unicode() exception:%s' %ex)
        return None
            

    def extract_element(self, a_str, element_list):
        '''
        抽取一个字符串的特定成分（ch, en, digit, other）
        @param element_list 需要保留的文本成分
        @return 处理后的字符串
        '''
        ele_mark = []   # 标识每个字符的成分
        for char in a_str:
            if uu.is_chinese(char):
                ele_mark.append('ch')
            elif uu.is_number(char):
                ele_mark.append('digit')
            elif uu.is_alphabet(char):
                ele_mark.append('en')
            elif uu.is_other_print_ascii(char):
                ele_mark.append('ascii')
            else:
                ele_mark.append('other')
        remove_char_idx = []
        for idx, mark in enumerate(ele_mark):
            if mark not in element_list:
                remove_char_idx.append(idx)
        return self.trim_str(a_str, remove_char_idx)

    
    def unicode_encode(self, a_str, encoding='utf-8'):
        '''
        unicode字符串编码
        '''
        if not isinstance(a_str, unicode):
            raise Exception, 'string encoding is not unicode.'
        return a_str.encode(encoding)


    def replace_substr(self, a_str):
        '''
        子串的替换，用str类的repalce进行替换
        '''
        for replace_info in self.cfg.replaces:
            from_strs = replace_info['from']
            to_str = replace_info['to']
            for from_str in from_strs.split(','):
                a_str = a_str.replace(from_str, to_str)
        return a_str


    def filter_repeated_substr(self, a_str):
        '''
        删除重复的子串
        '''
        substr_info = sa.find_dup_sub_str(a_str, self.cfg.rep_len, self.cfg.rep_times)
        #print 'repeated substrs:\n%s' %substr_info
        # [(sub-str, [(sIdx,eIdx), (sIdx,eIdx)]), ...]
        remove_char_idx = []
        for substr, idx_list in substr_info:
            start = 0
            end = len(idx_list)
            if self.cfg.rep_action == 'reservefirst':
                start = 1
            if self.cfg.rep_action == 'reservelast':
                end = len(idx_list)-1
            for (sIdx, eIdx) in idx_list[start:end]:
                for i in range(sIdx, eIdx+1):
                    remove_char_idx.append(i)
        return self.trim_str(a_str, remove_char_idx)

    
    def filter_brackets(self, a_str):
        '''
        删除匹配的括号
        @return 删除括号后的串
        '''
        brackets_info = self.find_all_brackets(a_str)
        if not brackets_info:   # 没有任何括号
            return a_str
        # 各类字段的下标
        ID_IDX = 0
        TEXT_IDX = 1
        BEGIN_IDX = 2
        END_IDX = 3
        POS_IDX = 0
        PAT_IDX = 1
        first_bracket_id = brackets_info[0][ID_IDX]
        first_bracket_begin = brackets_info[0][BEGIN_IDX]   # 第一个括号的首个字符下标
        last_bracket_id = brackets_info[-1][ID_IDX]
        last_bracket_end =  brackets_info[-1][END_IDX]  # 最后一个括号的末尾字符下标
        remove_char_idx = [] # 待删除的字符下标
        for bracket in brackets_info:
            id = bracket[ID_IDX]
            text = bracket[TEXT_IDX]
            content = a_str[bracket[BEGIN_IDX]+1:bracket[END_IDX]]
            expect_pos_list = self.brackets[text][POS_IDX]
            expect_pat_list = self.brackets[text][PAT_IDX]
            if ('anywhere' in expect_pos_list) or \
                ('begin' in expect_pos_list and id == first_bracket_id and first_bracket_begin == 0) or \
                ('end' in expect_pos_list and id == last_bracket_id and last_bracket_end == (len(a_str)-1)):
                if self.is_match(content, expect_pat_list):
                    for idx in range(bracket[BEGIN_IDX], bracket[END_IDX]+1):
                        remove_char_idx.append(idx)
        return self.trim_str(a_str, remove_char_idx) 


    def is_match(self, text, pat_list):
        for pat in pat_list:
            if pat.match(text):
                return True
        return False            


    def filter_chars(self, a_str):
        '''
        过滤字符，删除出现在开头的begin_chars，出现在末尾的end_chars，
        出现在任意位置的anywhere_chars

        @return 删除后的串
        '''
        brackets_info = self.find_all_brackets(a_str)
        brackets_region = set() # 符号及其内容所在的区域
        BEGIN_IDX = 2
        END_IDX = 3
        for info in brackets_info:
            for i in range(info[BEGIN_IDX], info[END_IDX]+1):
                brackets_region.add(i)
        remove_char_idx = []    # 待删除的字符下标
        if self.cfg.chars_begin:
            for idx, char in enumerate(a_str):
                if idx in brackets_region or char not in self.cfg.chars_begin:
                    break
                else:
                    remove_char_idx.append(idx)
        if self.cfg.chars_end:
            for idx in range(0, len(a_str))[::-1]:
                char = a_str[idx]
                if idx in brackets_region or char not in self.cfg.chars_end:
                    break
                else:
                    remove_char_idx.append(idx)
        if self.cfg.chars_anywhere:
            for idx, char in enumerate(a_str):
                if idx in brackets_region:
                    continue
                elif char in self.cfg.chars_anywhere:
                    remove_char_idx.append(idx)
        return self.trim_str(a_str, remove_char_idx)                    


    def trim_str(self, a_str, remove_char_idx):
        '''
        从a_str中删除remove_char_idx对应下标的字符
        '''
        new_str = ''
        for idx, char in enumerate(a_str):
            if idx not in remove_char_idx:
                new_str += char
        return new_str                


    def find_all_brackets(self, a_str):
        '''
        查找所有括号，返回每个括号的(id, text, begin, end)，并按begin排序
        [(id, '[]', begin, end), (id, '[]', begin, end)...]
        @return 失败或找不到返回[], 否则返回列表
        '''
        res = []
        if not a_str:
            return res
        id = 1
        begin = 0
        end = 0
        # 为方便查找，新建map: <左括号, 右括号>
        bracket_map = {}
        for key in self.brackets.keys():
            bracket_map[key[0]] = key[1]
        left_barcket = None            
        right_bracket = None            
        for idx, char in enumerate(a_str):
            if char in bracket_map:
                begin = idx
                left_bracket = char
                right_bracket = bracket_map[char]
            elif char == right_bracket:
                end = idx
                res.append((id, '%s%s' %(left_bracket, right_bracket), begin, end))
                id += 1
                left_barcket = None
                right_bracket = None
        return res


    def handle_brackets_config(self, cfg):
        '''
        bracket配置中的reg表达式进行编译，并转化为map
        <[], ((anywhere), (Pattern1, Pattern2...))>
        '''
        res = {}
        for bracket in cfg.brackets:
            text_list = bracket['text'].split(',')
            pos_list = bracket['pos'].split(',')
            pat_list = self.load_pats(bracket)
            for text in text_list:
                res[text] = (pos_list, pat_list)
        return res        

    def load_pats(self, cfg):
        '''
        编译reg表达式
        '''
        res = []
        if 'reg' in cfg:
            pattern = re.compile(cfg['reg'])
            res.append(pattern)
        elif 'file' in cfg:
            patterns = self.load_pat_from_file(cfg['file'])
            res.extend(patterns)
        return res


    def load_pat_from_file(self, pat_file):
        '''
        从文件中加载正则表达式
        '''
        res = []
        for line in open(pat_file):
            line = line[:-1]    # 去掉换行符 
            res.append(re.compile(line))
        return res


if __name__ == '__main__':
    conf_file = 'config.xml'
    tool = TitleRewrite(conf_file)
    a_str_list = [u'【001】一个“惊喜”-撒旦索爱：小孕妻乖乖就擒 - 红薯小说', \
            u'天际网CEO称今年加大产品研发力度筹备上市_科技_腾讯网', \
            u'先答一套卷子，然后进行面试。一|天际网点评|天际网怎么样|若邻网', \
            u'[海盗美剧.hdmeiju.com]超人：钢铁之躯.man.of.steel.2013.720p.bluray.x264.bcehd-hdmeiju', \
            u'詹妮弗的肉体[面包电影网www.mb1895.com]（加长版，含幕后制作特辑）jennifer\'s body.2009.bluray.1080p', \
            u'【6v电影www.dy131.com】极速蜗牛bd中英双字1280高清', \
            u'【我们很洋气字幕组】131025 音乐银行 shinee everybody 中文字5E55', \
            u'【显赫家族&女汉子字幕组】131027_mbc真正的男人e29【韩语中字】', \
            u'?????-??-Powered by www.85vod.com', \
            u'1xxoo,xxoo,xxoo电影,xxoo小说,xxoo图片,xxoo网站,你懂的网站,...', \
            u'06A7(7025) ??????????????????(??) - RM12.12 : ????, ??????????!', \
            u'『08-11』【直播】伊甸园重建立计划_饥荒游戏吧_百度贴吧', \
            u'【100227YY】想……呃、、。。。YY歌菲版神话。。_刘亦菲吧_百度...', \
            u'【10月】JOJO的奇妙冒险 01【悠哈璃羽&JOJO奇妙冒险吧】 - 哔哩哔哩 - ( ?- ?)つロ 乾杯~ - bilibili.tv', \
            u'黑色牧马人 2014款 3.6 龙腾典藏版外观图片1240192(35/43)_太平洋汽车网', \
            u'黑心医院看看到底怎么黑……惨！惨！惨！！！！！！！！！！..._安徽吧_百度贴吧', \
            u'【原创】 叱咤苍穹。（斗破前传之八大家族） 另招八人。_斗破苍穹吧_百度贴吧', \

            u'【原创】 叱咤苍穹。<斗破前传之八大家族> 另招八人。_斗破苍穹吧_百度贴吧', 
    ]
    for a_str in a_str_list:
        print a_str
        print tool.rewrite_title(a_str)
        print '-'*40



