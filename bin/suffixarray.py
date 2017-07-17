#!/usr/bin/env python
# -*- coding:utf-8 -*-


def get_suffix_array(a_str):
    '''
    Generate suffix array for 'a_str'.

    @return suffix array for the 'a_str'
    '''
    res = []
    for i in range(0, len(a_str)):
        res.append((i, a_str[i:]))
    return res


def comm_prefix(id_str1, id_str2):
    '''
    找出两个字符串的"最长"公共前缀
    '''
    (id1, str1) = id_str1
    (id2, str2) = id_str2
    prefix = ''
    for i in range(0, min(len(str1), len(str2))):
        if str1[i] == str2[i]:
            prefix += str1[i]
        else:
            break
    if len(prefix) >= 1 and abs(id1-id2) >= 1:
        return prefix[:abs(id1 - id2)]
    else:
        return ''
                            

def find_all_occurrences(a_str, sub_str):
    '''
    找出一个子串所有出现的位置
    '''
    idx_list = []
    idx = a_str.find(sub_str)
    while idx != -1:
        idx_list.append((idx, idx+len(sub_str)-1))
        idx = a_str.find(sub_str, idx+len(sub_str))
    return idx_list


def find_all_dup_sub_str(a_str):
    '''
    Find all duplicated sub-string in 'a_str'.
    sub-string的长度从1开始
    sub-string间可能有包含关系

    @return all duplicated sub-string and its times, like:
    {<sub-str, [(sIdx, eIdx), (sIdx, eIdx)]>...}
    '''
    res = {}
    sa = sorted(get_suffix_array(a_str), key=lambda x:x[1])
    for i in range(0, len(sa)-1):
        comm_str = comm_prefix(sa[i], sa[i+1])
        if len(comm_str) >= 1:
            res[comm_str] = 0
    for comm_str in res.keys():
        idx_list = find_all_occurrences(a_str, comm_str)
        res[comm_str] = idx_list
    return res            


def find_dup_sub_str(a_str, len_region, times_region):
    '''
    找出所有的重复子串，以及出现的位置
    重复子串间不存在包含关系

    @len_region 长度范围[min, max]
    @times_region 次数范围[min, max]
    @return 所有重复的子串，以及每个子串的位置，按子串长度排序
    [(sub-str, [(sIdx,eIdx), (sIdx,eIdx)]), ...]
    '''
    (min_len, max_len) = len_region
    (min_times, max_times) =  times_region
    sub_strs = find_all_dup_sub_str(a_str)
    # 长度、出现次数的过滤
    res = {}
    for sub_str, idx_list in sub_strs.items():
        if min_len <= len(sub_str) <= max_len and \
            min_times <= len(idx_list) <= max_times:
            res[sub_str] = idx_list
    # 检测子串间的包含关系
    remove_sub_str = []
    res_list = sorted(res.items(), key=lambda x:len(x[0]))
    for i in range(0, len(res_list)-1):
        for j in range(i+1, len(res_list)):
            if res_list[j][0].find(res_list[i][0]) != -1:
                remove_sub_str.append(res_list[i][0])
                break
    for sub_str in remove_sub_str:
        del res[sub_str]
        #print 'del:%s' %sub_str
    return sorted(res.items(), key=lambda x:len(x[0]), reverse=True)
    
    



a_str = u'网站你，你懂的网站'
a_str = u'2012北京普通话考试报名时间,2012北京普通话考试报名时间,2012北京普通话考试报名入口,2012北京普通话考试报名入口,2012北京普通话考试?'
#print find_all_dup_sub_str(a_str)
find_dup_sub_str(a_str, (2,100), (3,10))



