#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author zhangxiang04@baidu.com
# @date 2013/12/11

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def is_chinese_symbol(uchar):
    """判断一个unicode是否是汉字标点符号 by yitengfei"""
    if (uchar >= u'\uff01' and uchar<=u'\uff1f') or \
            (uchar >= u'\u3001' and uchar<=u'\u3011'):
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or \
            (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def is_other_print_ascii(uchar):
    '''
    是否为可显示的ASCII码字符(除了数字、字母外)
    '''
    if (u'\u0020' <= uchar <= u'\u002f') or \
        (u'\u003a' <= uchar <= u'\u0040') or \
        (u'\u005b' <= uchar <= u'\u0060') or \
        (u'\u007b' <= uchar <= u'\u007e'):
        return True
    return False


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def B2Q(uchar):
    """半角转全角"""
    inside_code=ord(uchar)
    # 非半角字符
    if inside_code<0x0020 or inside_code>0x7e:
        return uchar
    # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
    if inside_code==0x0020:
        inside_code=0x3000
    else:
        inside_code+=0xfee0
    return unichr(inside_code)

def Q2B(uchar):
    """全角转半角"""
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    # 不是半角字符返回原来的字符        
    if inside_code<0x0020 or inside_code>0x7e:
        return uchar
    return unichr(inside_code)

def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])

def uniform(ustring):
    """格式化字符串，完成全角转半角"""
    return stringQ2B(ustring)

def codec(a_str, from_encoding=None, to_encoding=None):
    '''
    编码转换
    '''
    if isinstance(a_str, unicode):
        return a_str.encode(to_encoding)
    elif isinstance(a_str, str):
        return a_str.decode(from_encoding).encode(to_encoding)

def string2List(ustring):
    """将ustring按照中文，字母，数字分开"""
    res = {}
    for uchar in ustring:
        if is_chinese(uchar):
            res['ch'] = res.get('ch', '') + uchar
        elif is_chinese_symbol(uchar):
            res['chsymbol'] = res.get('chsymbol', '') + uchar
        elif is_number(uchar):
            res['digit'] = res.get('digit', '') + uchar
        elif is_alphabet(uchar):
            res['en'] = res.get('en', '') + uchar
        elif is_other_print_ascii(uchar):
            res['ascii'] = res.get('ascii', '') + uchar
        else:
            res['other'] = res.get('other', '') + uchar
    return res


if __name__=="__main__":
    #test Q2B and B2Q
    #for i in range(0x0020,0x007F):
    #    print Q2B(B2Q(unichr(i))),B2Q(unichr(i))

    #test uniform
    ustring=u'1234中国hello,人名ａ高频Ａ789  ^%$#@*()~!sf123sdgf'
    ustring=uniform(ustring)
    print ustring
    ret=string2List(ustring)
    print ret

    a_str = u'测试test'.encode('utf-8')
    print codec(a_str, 'utf-8', 'gbk')

    '''
    a_str = u'abd 23349~@*&^@#%^$#(_)|:}{P测试'
    for char in a_str:
        print char, 
        print is_other_print_ascii(char)
    '''


