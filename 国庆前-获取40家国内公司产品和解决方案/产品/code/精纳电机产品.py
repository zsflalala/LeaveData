import json
import requests
import pandas as pd
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


def parse_row_table(tbdata,startrow=1,startcol=1,rowkey=0):
    table_dic = {}
    cols = tbdata.columns.values.tolist()
    row_length = len(tbdata._stat_axis.values.tolist())
    
    for row in range(startrow,row_length):
        row_dic = {}
        if str(tbdata.loc[row,0]) == 'nan':
            continue
        if tbdata.loc[row,0] not in table_dic.keys():
            table_dic[tbdata.loc[row,0]] = []
        for col in range(startcol,cols[-1]+1):
            row_dic[tbdata.loc[rowkey,col]] = str(tbdata.loc[row,col])
        table_dic[tbdata.loc[row,0]].append(row_dic)
    table_dic = {tbdata.loc[rowkey,0]:table_dic}
    return table_dic

def parse_col_table(tbdata,startrow=1,startcol=1,colkey=0):
    table_dic = {}
    col_length = len(tbdata.columns.values.tolist())
    rows = tbdata._stat_axis.values.tolist()
    
    for col in range(startcol,col_length):
        col_dic = {}
        if str(tbdata.loc[1,col]) == 'nan':
            continue
        if tbdata.loc[1,col] not in table_dic.keys():
            table_dic[tbdata.loc[1,col]] = []
        for row in range(rows[0],rows[-1]+1):
            col_dic[tbdata.loc[row,0]] = str(tbdata.loc[row,col])
        table_dic[tbdata.loc[1,col]].append(col_dic)
    table_dic = {tbdata.loc[1,colkey]:table_dic}
    return table_dic

def renew_tbdata(tbdata):
    cols = list(tbdata)
    if tbdata.loc[0,0] == '机座号' or tbdata.loc[2,0] == '极数':
        for col in cols:
            if tbdata.loc[0,col] != tbdata.loc[1,col]:
                tbdata.loc[1,col] = tbdata.loc[0,col] + '-' + tbdata.loc[1,col]
        tbdata = tbdata.drop(index=[0])
    else:
        for col in cols:
            if tbdata.loc[1,col] != tbdata.loc[2,col]:
                tbdata.loc[2,col] = tbdata.loc[1,col] + '-' + tbdata.loc[2,col]
        tbdata = tbdata.drop(index=[0,1])
    return tbdata

def parse_page(pro_url,headers,FirstTypeName):
    pro_dic = {}
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//h1[@class="e_h1-48 s_subtitle"]/text()')[0].strip()
    pro_desc = tree.xpath('.//div[@class="e_richText-38 s_title clearfix"]//text()')
    pro_desc = ''.join([item.strip() for item in pro_desc])
    pro_img = tree.xpath('.//div[@class="sp-wrap"]//img/@src')[0]

    args = {}
    try:
        tbdata = pd.read_html(pro_url,encoding='utf-8')[0]
        if tbdata.loc[0,0] == tbdata.loc[1,0] and tbdata.loc[0,0] == tbdata.loc[2,0]:
            args = parse_row_table(renew_tbdata(tbdata),startrow=3,rowkey=2)
        elif tbdata.loc[0,0] == '机座号':
            args = parse_row_table(renew_tbdata(tbdata),startrow=2,rowkey=1)
        elif pro_name == '直流无刷电机':
            args = parse_col_table(renew_tbdata(tbdata),startrow=2,colkey=0)
        else:
            args = parse_row_table(tbdata)
    except Exception as e:
        pass

    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = FirstTypeName
    pro_dic['SecondType'] = ''
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = pro_desc
    pro_dic['ProductDetail']['Feature'] = ''
    pro_dic['ProductDetail']['Parameter'] = args
    return pro_dic

@logger.catch
def KINAVO(headers):
    final_dic = {'pro':[]}
    kina_url = 'https://www.kinavo.com/product/6/'
    resp = requests.get(url=kina_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    kind_urls,kind_names = [],[]
    a_list = tree.xpath('.//p[@class="e_text-4 s_title"]/a')
    for a in a_list:
        kind_urls.append(urljoin(kina_url,a.xpath('./@href')[0]))
        kind_names.append(a.xpath('./text()')[0].strip())

    for i in range(len(kind_urls)):
        url,name = kind_urls[i],kind_names[i]
        pro_urls = []
        
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//a[@class="e_button-15 s_button1 btn btn-primary "]')
        for a in a_list:
            pro_urls.append(urljoin(url,a.xpath('./@href')[0]))

        for pro_url in pro_urls:
            logger.info(f'now url: {pro_url}')
            pro_dic = parse_page(pro_url,headers,name)
            final_dic['pro'].append(pro_dic) 
            logger.info(f'已爬取{len(final_dic["pro"])}条数据,')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    final_dic = KINAVO(headers=headers)
    filename=f'精纳电机产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')