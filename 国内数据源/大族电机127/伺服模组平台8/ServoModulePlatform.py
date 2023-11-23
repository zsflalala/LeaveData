import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin


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

def parse_intro_table2(tbdata,startrow=1,startcol=2):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    
    # 处理列名
    for row in range(startrow,row_length):
        tbdata.loc[row,0] += f'({str(tbdata.loc[row,1])})'
        tbdata.loc[row,6] += f'({str(tbdata.loc[row,7])})'
        try:
            tbdata.loc[row,12] += f'({str(tbdata.loc[row,13])})'
        except Exception as e:
            pass

    end_col = [5,11,16]
    for row in range(startrow,row_length):
        row_dic = {}
        if tbdata.loc[0,0] not in table_dic.keys():
            table_dic[tbdata.loc[0,0]] = {}
        if tbdata.loc[row,0] not in table_dic[tbdata.loc[0,0]].keys():
            table_dic[tbdata.loc[0,0]][tbdata.loc[row,0]] = []
        for col in range(2,5):
            row_dic[tbdata.loc[0,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[0,0]][tbdata.loc[row,0]].append(row_dic)
    
        row_dic = {}
        if tbdata.loc[0,6] not in table_dic.keys():
            table_dic[tbdata.loc[0,6]] = {}
        if tbdata.loc[row,6] not in table_dic[tbdata.loc[0,6]].keys():
            table_dic[tbdata.loc[0,6]][tbdata.loc[row,6]] = []
        for col in range(8,11):
            row_dic[tbdata.loc[0,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[0,6]][tbdata.loc[row,6]].append(row_dic)

        row_dic = {}
        if tbdata.loc[0,12] not in table_dic.keys():
            table_dic[tbdata.loc[0,12]] = {}
        if tbdata.loc[row,12] not in table_dic[tbdata.loc[0,12]].keys():
            table_dic[tbdata.loc[0,12]][tbdata.loc[row,12]] = []
        for col in range(14,16):
            if str(tbdata.loc[row,col]) == 'nan':
                tbdata.loc[row,col] = 'nan'
            row_dic[tbdata.loc[0,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[0,12]][tbdata.loc[row,12]].append(row_dic)

    return table_dic

def parse_intro_table3(tbdata,startrow=2,startcol=1):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    
        
    for row in range(startrow,row_length):
        row_dic = {}
        if tbdata.loc[row,0] not in table_dic.keys():
            table_dic[tbdata.loc[row,0]] = []
        for col in range(startcol,colunm_length):
            row_dic[tbdata.loc[1,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[row,0]].append(row_dic)

    table_dic = {tbdata.loc[0,0]:{tbdata.loc[1,0]:table_dic}}
    return table_dic

def parse_arg_table(tbdata,startrow=0,startcol=1):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    

    rowkey = tbdata.loc[0,0]
    table_dic[rowkey] = []
    for row in range(startrow,row_length,8):
        rowkey = tbdata.loc[row,0]
        if rowkey not in table_dic.keys():
            table_dic[rowkey] = []
        for col in range(startcol,colunm_length):
            col_dic = {}
            for row2 in range(row+1,row+7):
                col_dic[tbdata.loc[row2,0]] = tbdata.loc[row2,col]
            table_dic[rowkey].append(col_dic)
    return table_dic

def parse_page(page_url,headers):
    # 产品标题 图片和特点
    tree = etree.HTML(requests.get(url=page_url,headers=headers).text)
    pro_name = tree.xpath('.//div[@class="base-info"]/div[1]/text()')[0].strip()
    pro_feature = tree.xpath('.//div[@class="base-info"]/div[3]//text()')
    pro_feature = ''.join([item.replace('\xa0','').strip() for item in pro_feature if item.strip()])
    pro_img = urljoin(page_url,tree.xpath('.//div[@class="img swiper-slide text-center"]/img/@src')[0])
    pro_basic = {'产品名称':pro_name,'产品特点':pro_feature,'产品图片':pro_img}
    pro_intro = {}
    pro_args = {}

    tbdatas = pd.read_html(page_url)
    pro_intro_text = tree.xpath('.//div[@class="content c1"]/text()')
    pro_intro_text = ''.join([item.strip() for item in pro_intro_text])
    pro_intro['介绍信息'] = pro_intro_text
    pro_intro_imgtree = tree.xpath('.//div[@class="content c1"]//img')
    if pro_intro_imgtree != []:
        pro_intro['型号表示方法'] = []
        for img in pro_intro_imgtree:
            pro_intro['型号表示方法'].append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_intro['table1'] = parse_intro_table2(renew_table_colindex(tbdatas[1]))
    pro_intro['table2'] = parse_intro_table3(renew_table_colindex(tbdatas[2]))

    pro_args_imgtree = tree.xpath('.//div[@class="content c2"]//img')
    if pro_args_imgtree != []:
        pro_args['参数图片'] = []
        for img in pro_args_imgtree:
            pro_args['参数图片'].append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_args['table'] = parse_arg_table(renew_table_colindex(tbdatas[-1]))
    pro_dic = {'基本信息':pro_basic,'产品介绍':pro_intro,'产品参数':pro_args}
    return pro_dic

def ServoModule(headers,filename='servo_module_platform.json'):
    final_dic = {}
    linear_url = 'https://www.hansmotor.com/products/26/c-26/'
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
        pro_dic = parse_page(page_url=pro_urls[index],headers=headers)
        final_dic[pro_names[index]] = pro_dic
        print(f'已爬取{index+1}/{length}条数据.')

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")
    return final_dic


if __name__ == "__main__":
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    ServoModule(headers=headers,filename='伺服模组平台.json')
