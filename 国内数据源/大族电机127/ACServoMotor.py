from loguru import logger
import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin
import numpy as np


def parse_col_table(tbdata,startrow=0):
    table_dic = {}
    flag = 0
    row_length = len(tbdata._stat_axis.values.tolist())
    row = startrow
    while row < row_length:
        dif_col = tbdata.loc[row,:]    
        dif_col = list(dict.fromkeys(dif_col))
        if np.nan in dif_col:
            dif_col.remove(np.nan)
        if len(dif_col) == 1:
            col_key = dif_col[0]
            table_dic[col_key] = {}
            chosedic = table_dic[col_key]
            flag = 1
            row += 1
            continue
        elif flag == 0:
            chosedic = table_dic
        
        if len(dif_col) and dif_col[0] not in chosedic.keys():
            chosedic[dif_col[0]] = {}
        if len(dif_col) == 2 and chosedic[dif_col[0]] == {}:
            chosedic[dif_col[0]] = dif_col[1]
        elif len(dif_col) == 3:
            try:
                chosedic[dif_col[0]][dif_col[1]] = dif_col[2]
            except Exception as e:
                print(chosedic[dif_col[0]])
                print(dif_col)
        elif len(dif_col) == 4:
            if dif_col[1] not in chosedic[dif_col[0]].keys():
                chosedic[dif_col[0]][dif_col[1]] = {}
            chosedic[dif_col[0]][dif_col[1]][dif_col[2]] = dif_col[3]
        elif len(dif_col) == 5:
            if dif_col[1] not in chosedic[dif_col[0]].keys():
                chosedic[dif_col[0]][dif_col[1]] = {}
            if dif_col[2] not in chosedic[dif_col[0]][dif_col[1]].keys():
                chosedic[dif_col[0]][dif_col[1]][dif_col[2]] = {}
            chosedic[dif_col[0]][dif_col[1]][dif_col[2]][dif_col[3]] = dif_col[4]
        row += 1
    return table_dic

def parse_arg_table1(tbdata):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())

    if tbdata.loc[1,0] == tbdata.loc[2,0]:
        startrow = 3
    else:
        startrow = 2
        
    # 处理左侧列名
    for row in range(startrow,row_length):
        tbdata.loc[row,0] += f'({tbdata.loc[row,1]})'
    for col in range(2,colunm_length):
        col_dic = {}
        for row in range(startrow,row_length):
            if str(tbdata.loc[row,col])  == 'nan':
                tbdata.loc[row,col] = 'nan'
            col_dic[tbdata.loc[row,0]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[1,col]] = col_dic
    table_dic = {tbdata.loc[0,0]:table_dic}
    return table_dic

def parse_arg_table2(tbdata,startrow=1,startcol=1):
    table_dic = {tbdata.loc[0][0]:{}}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())
    keys = tbdata.loc[startrow:,0]
    row_dif = list(dict.fromkeys(keys))

    # 以第0列为主键
    for rowkey in row_dif:
        table_dic[tbdata.loc[0][0]][rowkey] = {}
    for row in range(startrow,row_length):
        row_dic = {}
        for col in range(startcol,col_length):
            row_dic[tbdata.loc[0,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[0][0]][tbdata.loc[row,0]] = row_dic
    return table_dic

def parse_page(page_url,headers,typeName):
    # 产品标题 图片和特点
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@class="base-info"]/div[1]/text()')[0].strip()
    pro_feature = tree.xpath('.//div[@class="base-info"]/div[3]//text()')
    pro_feature = ''.join([item.replace('\xa0','').strip() for item in pro_feature if item.strip()])
    pro_img = urljoin(page_url,tree.xpath('.//div[@class="img swiper-slide text-center"]/img/@src')[0])
    pro_basic = {'产品名称':pro_name,'产品特点':pro_feature,'产品图片':pro_img}
    pro_intro = {}
    pro_args = {}
    
    if pro_name.endswith('驱动器'):
        pro_intro['img'] = []
        img_list = tree.xpath('.//div[@class="content c1"]//img')
        for img in img_list:
            pro_intro['img'].append(urljoin(page_url,img.xpath('./@src')[0]))

        pro_args['img'] = []
        img_list = tree.xpath('.//div[@class="content c2"]//img')
        for img in img_list:
            pro_args['img'].append(urljoin(page_url,img.xpath('./@src')[0]))
    else:
        tbdatas = pd.read_html(page_url)
        pro_intro_text = tree.xpath('.//div[@class="content c1"]//text()')
        pro_intro_text = ''.join([item.strip() for item in pro_intro_text])
        tbdata = tbdatas[0]
        pro_intro_table = parse_col_table(tbdata)
        pro_intro_img = urljoin(page_url,tree.xpath('.//div[@class="content c1"]//img/@src')[0]) 
        pro_intro['介绍信息'] = pro_intro_text
        pro_intro['使用环境'] = pro_intro_table
        pro_intro['命名规则'] = pro_intro_img

        pro_args['尺寸图'] = urljoin(page_url,tree.xpath('.//div[@class="content c2"]//img/@src')[0])
        pro_args['table1'] = parse_arg_table1(tbdatas[-2])
        pro_args['table2'] = parse_arg_table2(tbdatas[-1])

    pro_dic = {}
    pro_dic['ProductName'] = pro_basic['产品名称']
    pro_dic['ProductImage'] = pro_basic['产品图片']
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = typeName
    pro_dic['SecondType'] = ''
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_intro
    pro_dic['ProductDetail']['Feature'] = pro_basic['产品特点']
    pro_dic['ProductDetail']['Parameter'] = pro_args
    return pro_dic

def AC_Servo_Motor(headers,filename='AC_servo_motor.json',typeName='交流伺服电机'):
    final_dic = []
    linear_url = 'https://www.hansmotor.com/products/13/c-13/'
    tree = etree.HTML(requests.get(url=linear_url,headers=headers).text)
    div_lists = tree.xpath('//div[@class="product-list"]/div/div[@class="box fl text-center relative"]')
    pro_urls,pro_names = [],[]
    for div in div_lists:
        pro_url = urljoin(linear_url,div.xpath('./div[3]//a/@href')[0])
        pro_name = div.xpath('./div[2]/text()')[0]
        pro_names.append(pro_name)
        pro_urls.append(pro_url)
    length = len(pro_urls)

    for index in range(length):
        print(f'当前url: {pro_urls[index]},',end='  ')
        pro_dic = parse_page(page_url=pro_urls[index],headers=headers,typeName=typeName)
        final_dic.append(pro_dic) 
        print(f'已爬取{index+1}/{length}条数据.')
    return final_dic


if __name__ == "__main__":
    final_dic = {'pro':[]}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic['pro'] = AC_Servo_Motor(headers=headers)
    filename='交流伺服电机.json'
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f"爬取完成，存储在{filename}中.")
