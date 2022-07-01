#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import openpyxl
import os, re, timeit


frgb_res = 'FFAFAFAF'

glist = []

def write_to_file(regdict, wfd):
    if regdict['Addr'] in glist:
        return
    glist.append(regdict['Addr'])
    headstr = '\n/* Addr {} {} {} */\n'.format(regdict['Addr'], regdict['Mode'], regdict['Default'])
    temp = regdict['bit']
    wfd.write(headstr)
    wfd.write('union reg_{}'.format(regdict['Addr'].lower()) + ' {\n')
    wfd.write('\tuint32_t value;\n')
    wfd.write('\tstruct {\n')
    #
    bwid = 0
    rest = 0
    for i in range(32):
        if i not in temp.keys():
            if i == 31:
                # print(i, rest)
                rewid = i - rest + 1
                if rewid:
                    wfd.write('\t\tuint32_t : {};\n'.format(rewid))
            continue
        rewid = i - rest
        if rewid:
            wfd.write('\t\tuint32_t : {};\n'.format(rewid))
        rest = i
        bnm, bst, bed = temp[i].split('; ')
        bnm = bnm.lower()
        bnm = bnm.replace(' ', '_')
        bnm = bnm.replace('(', '_')
        bnm = bnm.replace(')', '')
        bwid = int(bed) - int(bst) + 1
        # print(i, temp[i], bnm, bst, bed, type(bnm), type(bst), type(bed), bwid)
        wfd.write('\t\tuint32_t {} : {};\n'.format(bnm, bwid))
        rest = int(bed) + 1
        pass
    #
    wfd.write('\t} bits;\n')
    wfd.write('};\n')
    pass


def parse_single_table(tabs, cter, rowCnt, wfd):
    regDict = {}
    bitDict = {}
    regDict['bit'] = bitDict
    bst = -1
    bed = -1
    for idxr, curRow in enumerate(tabs[:-1]):
        curRowVal = [x.value for x in curRow[:cter]]
        nextRow = tabs[idxr + 1]
        nextRowVal = [x.value for x in nextRow[:cter]]
        # print(curRowVal, '\n-->', nextRowVal)
        if curRowVal[0] == '... repeated until ...':
            if bitDict:
                write_to_file(regDict, wfd)
                regDict = {}
                bitDict = {}
                regDict['bit'] = bitDict
            wfd.write('\n/* ... repeated until ... */\n')
            continue
        if curRowVal[2] == 31:
            if bitDict:
                write_to_file(regDict, wfd)
                regDict = {}
                bitDict = {}
                regDict['bit'] = bitDict
            regDict['Addr'] = nextRowVal[0]
            regDict['Mode'] = nextRowVal[1]
            regDict['Default'] = nextRowVal[-1]
            pass
        # 其他标签行
        if curRowVal[2] in range(32):
            # 解析field 字段，遍历列
            curCell = curRow[2:cter - 1]
            nextCell = nextRow[2:cter - 1]
            flag = -1
            for idxc, cell in enumerate(curCell):
                if flag != -1 and idxc < flag:
                    continue
                if nextCell[idxc].fill.fgColor.rgb == frgb_res:
                    continue
                bed = cell.value
                # bst = bed
                flag = idxc
                bnm = nextCell[idxc].value
                while flag < len(curCell) - 1 and isinstance(nextCell[flag + 1].value, type(None)):
                    if nextCell[flag + 1].fill.fgColor.rgb == frgb_res:
                        break
                    flag += 1
                bst = curCell[flag].value
                if not isinstance(bnm, type(None)):
                    bitDict[bst] = '{}; {}; {}'.format(bnm, bst, bed)
            pass
        pass
    # 写字典到文件
    # print('to write', regDict)
    write_to_file(regDict, wfd)
    pass



def parse_excel(rdir, sfile, wfd):
    start2 = timeit.default_timer()
    wkbook = openpyxl.load_workbook(os.path.join(rdir, sfile), read_only=True)
    end2 = timeit.default_timer()
    print('load ', end2 - start2)
    #
    start2 = timeit.default_timer()
    ws = wkbook.active
    end2 = timeit.default_timer()
    # print('load-2 ', end2 - start2)
    rowList = [x for x in ws.rows]
    #
    # 2.1 定位单个reg table
    # newRowList = rowList[1022:1034]
    # newRowList = rowList[1425:1429]
    # newRowList = rowList[26320:26330]
    newRowList = rowList
    for idxr, curRow in enumerate(newRowList):
        if curRow[0].value == '... repeated until ...':
            # wfd.write('\n/* ... repeated until ... */\n')
            continue
        if not curRow[0].value == 'Addr':
            continue
        # 第1行，获取截至列，预计多少行
        curRowVals = [x.value for x in curRow]
        cter = len(curRowVals)
        while curRowVals[cter - 1] != 'Default':
            cter -= 1
        # 获取截至行
        rowCnt = 0
        strow = curRow
        while True:
            stcell = [x.value for x in strow[:cter]]
            nextRow = newRowList[idxr + rowCnt + 1]
            nextcell = [x.value for x in nextRow[:cter]]
            next2Row = newRowList[idxr + rowCnt + 2]
            next2cell = [x.value for x in next2Row[:cter]]
            rowCnt += 1
            # print(idxr, cnt, rowCnt, cter, stcell, '\n---->', nextcell)
            if stcell[2] in range(32) and (not nextcell[2] in range(32)):
                if next2cell[0] == '... repeated until ...':
                    continue
                elif not next2cell[2] in range(32):
                    rowCnt += 1
                    break
        # 处理单个table
        # print(idxr, rowCnt, cter, '----------------------------------------')
        parse_single_table(newRowList[idxr:idxr + rowCnt], cter, rowCnt, wfd)
    pass



def remove_redundant_label(raw, rdir, fnm):
    subraw = raw
    #
    ptrn = re.compile(r'<style [\s\S]*?</style>')  # 删除页面 style
    while re.search(ptrn, subraw):
        # print(re.search(ptrn, subraw).group())
        subraw = re.sub(ptrn, '', subraw)
    #
    ptrn = re.compile(r'style=\"[\s\S]*?";*')  # 删除行内style
    while re.search(ptrn, subraw):
        # print(re.search(ptrn, subraw).group())
        subraw = re.sub(ptrn, '', subraw)
    #
    ptrn = re.compile(r'<p [\s\S]*?;*>')  # 删除 P 标签
    while re.search(ptrn, subraw):
        # print(re.search(ptrn, subraw).group())
        subraw = re.sub(ptrn, '', subraw)
    ptrn = re.compile(r'<p>')
    while re.search(ptrn, subraw):
        # print(re.search(ptrn, subraw).group())
        subraw = re.sub(ptrn, ' ', subraw)
    ptrn = re.compile(r'</p>')
    while re.search(ptrn, subraw):
        # print(re.search(ptrn, subraw).group())
        subraw = re.sub(ptrn, ' ', subraw)
    #
    ptrn = re.compile(r'\s+>')  # 删除 标签中空格
    while re.search(ptrn, subraw):
        # print(re.search(ptrn, subraw).group())
        subraw = re.sub(ptrn, '>', subraw)
    # write file
    with open(os.path.join(rdir, fnm), 'w', encoding='utf-8') as wfd:
        wfd.write(subraw)
    return subraw

def main(srcfile):
    rdir = os.path.split(os.path.abspath(srcfile))[0]
    fnm, suffix = os.path.splitext(srcfile)
    print('--1--', rdir, fnm, suffix)
    # 1 获取raw data
    with open(os.path.join(rdir, srcfile), 'r', encoding='utf-8') as rfd:
        raw = rfd.read()

    # 2 剔除不重要的标签
    raw2 = remove_redundant_label(raw, rdir, '{}-temp-1.htm'.format(fnm))

    # 3 手动打开生成的htm文件，全选并新建excel表格并命名为《Register_Map-temp-2.xlsx》，进行存放
    with open(os.path.join(rdir, '{}-temp-3.h'.format(fnm)), 'w', encoding='utf-8') as wfd:
        parse_excel(rdir, '{}-temp-2.xlsx'.format(fnm), wfd)

    # 4 校验

    pass


if __name__ == '__main__':
    rdir = os.getcwd()
    main('Register_Map.htm')
