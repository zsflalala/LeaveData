from loguru import logger
import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin
import numpy as np


def renew_table_colindex(tbdata):
    col_length = len(tbdata.columns.values.tolist())
    # 数据头索引不是 0 - 5 构成 重新创建
    col_index = tbdata.columns.values.tolist()
    if 0 not in col_index:
        first_row = {}
        for i in range(col_length):
            first_row[i] = col_index[i]
            tbdata = tbdata.rename(columns={col_index[i]:i})
        dfhead = pd.DataFrame(first_row,index=[0])
        tbdata = dfhead._append(tbdata, ignore_index = True)
    return tbdata

def parse_col_table1(tbdata,startrow=1,startcol=1):
    table_dic = {}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())
    row = startrow

    # 处理列名
    for row in range(startrow,row_length-1):
        tbdata.loc[row,0] += f'({tbdata.loc[row,1]})'
    colkey_list = []
    # 获取colkey作为列表
    for col in range(startcol+1,col_length):
        if tbdata.loc[startrow-1,col] != tbdata.loc[startrow-1,col-1]:
            colkey_list.append(col)
    colkey_list.append(col_length)
        
    rowkey = tbdata.loc[startrow-1,startcol]
    colid = 0
    for col in range(startcol,col_length):
        if col == colkey_list[colid]:
            colid += 1
        rowkey = tbdata.loc[startrow-1,colkey_list[colid]-1]
        col_dic = {}
        for row in range(startrow,row_length-1):
            col_dic[tbdata.loc[row,0]] = tbdata.loc[row,col]
        if rowkey not in table_dic.keys():
            table_dic[rowkey] = []
        table_dic[rowkey].append(col_dic)
    table_dic['备注'] = tbdata.loc[row_length-1,0]
    return table_dic

def parse_col_table2(tbdata,startrow=1,startcol=1):
    table_dic = {}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())

    for row in range(startrow,row_length):
        if tbdata.loc[row,1] != tbdata.loc[row,col_length-1]:
            rowkey = row - 1
            table_dic[tbdata.loc[rowkey,0]] = []
            break
    for col in range(startcol,col_length):
        col_dic = {}
        for row in range(startrow,row_length):
            col_dic[tbdata.loc[row,0]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[rowkey,0]].append(col_dic)
    return table_dic

def parse_LML_table1(tbdata,startrow=1,startcol=2):
    table_dic = {}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())

    # 处理列名
    for row in range(startrow,row_length-1):
        tbdata.loc[row,0] += f'({tbdata.loc[row,1]})'

    for col in range(startcol,col_length-1):
        col_dic = {}
        for row in range(startrow,row_length):
            col_dic[tbdata.loc[row,0]] = tbdata.loc[row,col]
        if tbdata.loc[startrow,startcol] not in table_dic.keys():
            table_dic[tbdata.loc[startrow,startcol]] = []
        table_dic[tbdata.loc[startrow,startcol]].append(col_dic)

    return table_dic

def parse_LMH_table1(tbdata,startrow=1,startcol=2):
    table_dic = {}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())
    row = startrow

    # 处理列名
    for row in range(startrow,row_length-1):
        tbdata.loc[row,0] += f'({tbdata.loc[row,1]})'
        
    rowkey = tbdata.loc[startrow-1,startcol]
    for col in range(startcol,col_length):
        col_dic = {}
        for row in range(startrow,row_length):
            col_dic[tbdata.loc[row,0]] = tbdata.loc[row,col]
        if rowkey not in table_dic.keys():
            table_dic[rowkey] = []
        table_dic[rowkey].append(col_dic)
    return table_dic

# 产品信息
def parse_LMA_basic(page_url,tree):
    pro_name = tree.xpath('.//div[@class="base-info"]/div[1]/text()')[0].strip()
    pro_feature = tree.xpath('.//div[@class="base-info"]/div[3]//text()')
    pro_feature = ''.join([item.replace('\xa0','').strip() for item in pro_feature if item.strip()])
    pro_imgs = tree.xpath('//div[@class="swiper-container gallery-thumbs"]/div//img')
    pro_img = []
    for img in pro_imgs:
        pro_img.append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_basic = {'产品名称':pro_name,'产品特点':pro_feature,'产品图片':pro_img}
    return pro_basic

def parse_LMA_intro(page_url,tree):
    titles = tree.xpath('//div[@class="content c1"]//strong')
    first_title = titles[0].xpath('.//text()')
    first_title = ''.join([item.strip().replace(' ','') for item in first_title if item.strip()])
    
    first_title_txt = tree.xpath('//div[@class="content c1"]//text()')
    first_title_txt = ''.join(item.strip().replace('\xa0','').replace(' ','') for item in first_title_txt if item.strip()).replace(first_title,'')
    second_title = titles[1].xpath('.//text()')[0]
    second_title_img = urljoin(page_url,tree.xpath('//div[@class="content c1"]//img/@src')[0])
    pro_intro = {first_title:first_title_txt,second_title:second_title_img}
    return pro_intro

def parse_LMA_args(page_url,tree):
    table_dic = {}
    text = tree.xpath('//div[@class="content c2"]/span//text()')
    text = ''.join(item.strip() for item in text if item.strip())
    table_dic['text'] = text

    tbdata = pd.read_html(page_url)
    if len(tbdata) == 1:
        tbdata = tbdata[0]
        table_dic[tbdata.loc[0,0]] = {}
        row_length = len(tbdata._stat_axis.values.tolist())
        
        # 处理左侧列名,并存入数据
        title_row = 0
        for row in range(2,row_length-1):
            if tbdata.loc[row,0] == tbdata.loc[row,2]:
                table_dic[tbdata.loc[0,0]][tbdata.loc[row,0]] = {}
                title_row = row
                continue
            tbdata.loc[row,0] += " " + tbdata.loc[1,1] + ': ' +  tbdata.loc[row,1]
            table_dic[tbdata.loc[0,0]][tbdata.loc[title_row,0]][tbdata.loc[row,0]] = tbdata.loc[row,2]
        table_dic[tbdata.loc[0,0]]['备注'] = tbdata.loc[row_length-1,2]
        return table_dic

    elif len(tbdata) == 2:
        tbdata0,tbdata1 = tbdata[0],tbdata[1]
        row_length0 = len(tbdata0._stat_axis.values.tolist())
        row_length1 = len(tbdata1._stat_axis.values.tolist())

        col_index1 = tbdata1.columns.values.tolist()
        if 0 not in col_index1:
            colunm_length1 = len(tbdata1.columns.values.tolist())
            first_row = {}
            for i in range(colunm_length1):
                first_row[i] = col_index1[i]
                tbdata1 = tbdata1.rename(columns={col_index1[i]:i})
            dfhead = pd.DataFrame(first_row,index=[0])
            tbdata1 = dfhead._append(tbdata1, ignore_index = True)
            row_length1 = len(tbdata1._stat_axis.values.tolist())

        table_dic['电机型号及参数'] = {}
        table_dic['电机型号及参数']['电机参数'] = {}
        table_dic['电机型号及参数']['平台参数'] = {}

        if tbdata0.loc[0,0] == '电机型号及参数':
            row = 3
        else:
            row = 2
        while row < row_length0:
            tbdata0.loc[row,0] += ' 单位: ' +  tbdata0.loc[row,1]
            table_dic['电机型号及参数']['电机参数'][tbdata0.loc[row,0]] = tbdata0.loc[row,2]
            row += 1

        row = 2
        while row < row_length1:
            if row == row_length1 - 1:
                table_dic['电机型号及参数']['平台参数']['备注'] = tbdata1.loc[row,2]
                break
            tbdata1.loc[row,0] += ' 单位: ' +  tbdata1.loc[row,1]
            table_dic['电机型号及参数']['平台参数'][tbdata1.loc[row,0]] = tbdata1.loc[row,2]
            row += 1
        return table_dic
    return None

def parse_LMA_page(page_url,headers,typeName,secondTypeName):
    pro_dic = {}
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_basic = parse_LMA_basic(page_url=page_url,tree=tree)
    pro_intro = parse_LMA_intro(page_url=page_url,tree=tree)
    pro_args = parse_LMA_args(page_url=page_url,tree=tree)

    pro_dic = {}
    pro_dic['ProductName'] = pro_basic['产品名称']
    pro_dic['ProductImage'] = pro_basic['产品图片']
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = typeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_intro
    pro_dic['ProductDetail']['Feature'] = pro_basic['产品特点']
    pro_dic['ProductDetail']['Parameter'] = pro_args
    return pro_dic


def parse_LMB_basic(page_url,tree):
    pro_name = tree.xpath('.//div[@class="base-info"]/div[1]/text()')[0].strip()
    pro_feature = tree.xpath('.//div[@class="base-info"]/div[3]//text()')
    pro_feature = ''.join([item.replace('\xa0','').strip() for item in pro_feature if item.strip()])
    pro_imgs = tree.xpath('//div[@class="thumb"]//img')
    pro_img = []
    for img in pro_imgs:
        pro_img.append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_basic = {'产品名称':pro_name,'产品特点':pro_feature,'产品图片':pro_img}
    return pro_basic

def parse_LMB_args(page_url,tree):
    table_dic = {}
    text = tree.xpath('//div[@class="content c2"]/span//text()')
    text = ''.join(item.strip() for item in text if item.strip())
    if text == '':
        text = tree.xpath('//div[@class="content c2"]//text()')
        text = ''.join(item.strip() for item in text if item.strip())
    table_dic['text'] = text

    tbdata = pd.read_html(page_url)
    tbdata0,tbdata1 = tbdata[0],tbdata[1]
    row_length0 = len(tbdata0._stat_axis.values.tolist())
    row_length1 = len(tbdata1._stat_axis.values.tolist())
    colunm_length1 = len(tbdata1.columns.values.tolist())

    table_dic[tbdata0.loc[0,0]] = {tbdata0.loc[1,0]:{}}
    row = 2
    while row < row_length0:
        if row == row_length0 - 1:
            table_dic[tbdata0.loc[0,0]]['备注'] = tbdata0.loc[row,2]
            break
        tbdata0.loc[row,0] += ' 单位：' + tbdata0.loc[row,1]
        table_dic[tbdata0.loc[0,0]][tbdata0.loc[row,0]] = tbdata0.loc[row,2]
        row += 1
    table_dic[tbdata1.loc[0,0]] = {}
    row = 1
    while row < row_length1:
        col_list = []
        for col in range(1,colunm_length1):
            col_list.append(tbdata1.loc[row,col])
        table_dic[tbdata1.loc[0,0]][tbdata1.loc[row,0]] = col_list
        row += 1
    return table_dic

def parse_LMB_page(page_url,headers,typeName,secondTypeName):
    pro_dic = {}
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_basic = parse_LMB_basic(page_url=page_url,tree=tree)
    pro_intro = parse_LMA_intro(page_url=page_url,tree=tree)
    pro_args = parse_LMB_args(page_url=page_url,tree=tree)
    pro_dic = {}
    pro_dic['ProductName'] = pro_basic['产品名称']
    pro_dic['ProductImage'] = pro_basic['产品图片']
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = typeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_intro
    pro_dic['ProductDetail']['Feature'] = pro_basic['产品特点']
    pro_dic['ProductDetail']['Parameter'] = pro_args
    return pro_dic


def parse_LM_args(page_url,tree,series):
    table_dic = {}
    title = tree.xpath('//div[@class="content c2"]/p//strong//text()')
    title = ''.join(item.strip() for item in title if item.strip())
    text = tree.xpath('//div[@class="content c2"]/p//text()')
    text = ''.join(item.strip() for item in text if item.strip())
    table_dic['text'] = text
    table_dic['直线电机平台参数'] = []

    tbdatas = pd.read_html(page_url)
    for i in range(len(tbdatas)):
        tbdata = tbdatas[i]
        tbdata = renew_table_colindex(tbdata)
        
        if '单位' in list(tbdata.iloc[:,1]):
            if tbdata.loc[0,0] not in table_dic.keys():
                if series == 2:
                    table_dic[tbdata.loc[0,0]]= parse_col_table1(tbdata,startrow=2,startcol=2)
                elif series == 3:
                    table_dic[tbdata.loc[0,0]]= parse_col_table1(tbdata,startrow=3,startcol=2)
                elif series == 4:
                    if '电机型号及参数' in list(tbdata.loc[1,:]):
                        startrow = 2
                    elif '电机型号及参数' in list(tbdata.loc[0,:]):
                        startrow = 1
                    table_dic[tbdata.loc[0,0]]= parse_LML_table1(tbdata,startrow=startrow,startcol=2)
            else:
                tbdata.loc[0,0] += f'({i})'
                table_dic[tbdata.loc[0,0]]= parse_col_table1(tbdata,startrow=2,startcol=2)
        else:
            if series == 4:
                table_dic['直线电机平台参数'].append(parse_col_table2(tbdata,startrow=2))
            else:
                table_dic['直线电机平台参数'].append(parse_col_table2(tbdata))
    return table_dic

def parse_LM_page(page_url,headers,series,typeName,secondTypeName):
    pro_dic = {}
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_basic = parse_LMB_basic(page_url=page_url,tree=tree)
    pro_intro = parse_LMA_intro(page_url=page_url,tree=tree)
    pro_args = parse_LM_args(page_url=page_url,tree=tree,series=series)
    pro_dic = {}
    pro_dic['ProductName'] = pro_basic['产品名称']
    pro_dic['ProductImage'] = pro_basic['产品图片']
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = typeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_intro
    pro_dic['ProductDetail']['Feature'] = pro_basic['产品特点']
    pro_dic['ProductDetail']['Parameter'] = pro_args
    return pro_dic


def parse_LMD_table1(tbdata,startrow=1,startcol=1):
    table_dic = {tbdata.loc[0][0]:{}}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())
    keys = tbdata.loc[startrow:,0]
    row_dif = list(dict.fromkeys(keys))

    # 以第0列为主键
    for rowkey in row_dif:
        table_dic[tbdata.loc[0][0]][rowkey] = []
    for row in range(startrow,row_length):
        row_dic = {}
        for col in range(startcol,col_length):
            row_dic[tbdata.loc[0,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[0][0]][tbdata.loc[row,0]].append(row_dic)
    return table_dic

def parse_LMD_intro(page_url,tree):
    titles = tree.xpath('//div[@class="content c1"]//strong')
    first_title = titles[0].xpath('.//text()')
    first_title = ''.join([item.strip().replace(' ','') for item in first_title if item.strip()])
    first_title_txt = tree.xpath('//div[@class="content c1"]//text()')
    first_title_txt = ''.join(item.strip().replace('\xa0','').replace(' ','') for item in first_title_txt if item.strip()).replace(first_title,'')
    pro_intro = {first_title:first_title_txt}
    return pro_intro

def parse_LMD_args(page_url,tree):
    table_dic = {}
    text = tree.xpath('//div[@class="content c2"]/text()')
    text = ''.join(item.strip() for item in text if item.strip())
    table_dic['text'] = text
    
    tbdatas = pd.read_html(page_url)
    assert len(tbdatas) == 2
    for i in range(len(tbdatas)):
        tbdata = tbdatas[i]
        tbdata = renew_table_colindex(tbdata)
        if i == 0:
            table_dic['table1'] = parse_LMD_table1(tbdata)
        elif i == 1:
            table_dic['table2'] = parse_col_table2(tbdata)

    return table_dic

def parse_LMD_page(page_url,headers,series,typeName,secondTypeName):
    pro_dic = {}
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_basic = parse_LMB_basic(page_url=page_url,tree=tree)
    pro_intro = parse_LMD_intro(page_url=page_url,tree=tree)
    pro_args = parse_LMD_args(page_url=page_url,tree=tree)
    pro_dic = {}
    pro_dic['ProductName'] = pro_basic['产品名称']
    pro_dic['ProductImage'] = pro_basic['产品图片']
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = typeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_intro
    pro_dic['ProductDetail']['Feature'] = pro_basic['产品特点']
    pro_dic['ProductDetail']['Parameter'] = pro_args
    return pro_dic


def parse_LMH_args(page_url,tree):
    table_dic = {}
    text = tree.xpath('//div[@class="content c2"]/text()')
    text = ''.join(item.strip() for item in text if item.strip())
    table_dic['text'] = text
    
    tbdatas = pd.read_html(page_url)
    if len(tbdatas) == 2:
        tbdata = tbdatas[0]
        tbdata = renew_table_colindex(tbdata)
        table_dic[tbdata.loc[0,0]] = {}
        table_dic[tbdata.loc[0,0]] = parse_col_table1(tbdata,startrow=3,startcol=2)

    elif len(tbdatas) == 1:
        tbdata = tbdatas[0]
        tbdata = renew_table_colindex(tbdata)
        table_dic[tbdata.loc[0,0]] = {}
        row_length = len(tbdata._stat_axis.values.tolist())
        slice_startrow = 0
        flag = 1
        for row in range(row_length):
            dif_col = tbdata.loc[row,:]    
            dif_col = list(dict.fromkeys(dif_col))
            if np.nan in dif_col:
                dif_col.remove(np.nan)
            if len(dif_col) == 0 and flag == 1:
                slice_tbdata = tbdata.loc[slice_startrow:row-1,:]
                table_dic[tbdata.loc[0,0]] = parse_LMH_table1(slice_tbdata,startrow=3,startcol=2)
                slice_startrow = row + 1
                flag = 0

    return table_dic

def parse_LMH_page(page_url,headers,series,typeName,secondTypeName):
    pro_dic = {}
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_basic = parse_LMB_basic(page_url=page_url,tree=tree)
    pro_intro = parse_LMD_intro(page_url=page_url,tree=tree)
    pro_args = parse_LMH_args(page_url=page_url,tree=tree)
    pro_dic = {}
    pro_dic['ProductName'] = pro_basic['产品名称']
    pro_dic['ProductImage'] = pro_basic['产品图片']
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = typeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_intro
    pro_dic['ProductDetail']['Feature'] = pro_basic['产品特点']
    pro_dic['ProductDetail']['Parameter'] = pro_args
    return pro_dic

def parse_series_page(series_kind,page_url,headers,typeName,secondTypeName):
    if series_kind == 0:
        return parse_LMA_page(page_url=page_url,headers=headers,typeName=typeName,secondTypeName=secondTypeName)
    elif series_kind == 1:
        return parse_LMB_page(page_url=page_url,headers=headers,typeName=typeName,secondTypeName=secondTypeName)
    elif series_kind == 2:
        return parse_LM_page(page_url=page_url,headers=headers,series=series_kind,typeName=typeName,secondTypeName=secondTypeName)
    elif series_kind == 3:
        return parse_LM_page(page_url=page_url,headers=headers,series=series_kind,typeName=typeName,secondTypeName=secondTypeName)
    elif series_kind == 4:
        return parse_LM_page(page_url=page_url,headers=headers,series=series_kind,typeName=typeName,secondTypeName=secondTypeName)
    elif series_kind == 5:
        return parse_LMH_page(page_url=page_url,headers=headers,series=series_kind,typeName=typeName,secondTypeName=secondTypeName)
    elif series_kind == 6:
        return parse_LMD_page(page_url=page_url,headers=headers,series=series_kind,typeName=typeName,secondTypeName=secondTypeName)
    return None

def DirectDriveMotor(headers,filename='direct_drive_motor.json',use_proxies=False,typeName='直驱电机'):
    dd_url = 'https://www.hansmotor.com/products/5/c-5/'
    if use_proxies:
        proxies = {"http": "http://27.192.168.73"}
    else:
        proxies = None 
    resp = requests.get(dd_url,headers=headers,proxies=proxies)

    if resp.status_code != 200:
        print('状态码: ',resp.status_code)
        return None
    tree = etree.HTML(resp.text)

    # 系列页面
    pro_series_urls,pro_series_names = [],[]
    a_lists = tree.xpath('/html/body/div[3]/div[1]/div[1]/div[3]/div/a')
    for a in a_lists:
        pro_series_urls.append(urljoin(dd_url,a.xpath('./@href')[0]))
        pro_series_names.append(a.xpath('./text()')[0])
    
    final_dic = []
    for index in range(len(pro_series_urls)):
        pro_series_url = pro_series_urls[index]
        pro_series_name = pro_series_names[index]
        series_resp = requests.get(url=pro_series_url,headers=headers)
        series_tree = etree.HTML(series_resp.text)
        pro_urls,pro_names = [],[]

        # 系列内产品页面
        div_lists = series_tree.xpath('//div[@class="product-list"]/div/div[@class="box fl text-center relative"]')
        for div in div_lists:
            pro_names.append(div.xpath('./div[2]/text()')[0])
            pro_urls.append(urljoin(pro_series_url,div.xpath('./div[3]//a/@href')[0]))
        length = len(pro_urls)
        print(pro_series_name,pro_series_url,len(pro_urls))

        for i in range(length):
            print('当前页面是：',pro_urls[i]," 进度: ",i + 1,'/',length)
            pro_dic = parse_series_page(series_kind=index,page_url=pro_urls[i],headers=headers,typeName=typeName,secondTypeName=pro_series_name)
            final_dic.append(pro_dic)
    return final_dic

if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    final_dic['pro'] = DirectDriveMotor(headers=headers,use_proxies=False)
    filename='直驱电机.json'
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f"爬取完成，存储在{filename}中.")


