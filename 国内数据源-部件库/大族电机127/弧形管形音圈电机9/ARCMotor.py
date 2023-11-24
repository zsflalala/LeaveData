import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin


def parse_arg_table(tbdata):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())

    if tbdata.loc[1,0].startswith('初级规格'):
        startrow = 3
    else:
        startrow = 2
        
    # 处理左侧列名
    for row in range(startrow,row_length):
        tbdata.loc[row,0] += f'({tbdata.loc[row,1]}:{tbdata.loc[row,2]})'
    for col in range(3,colunm_length):
        col_dic = {}
        for row in range(startrow,row_length):
            col_dic[tbdata.loc[row,0]] = tbdata.loc[row,col]
        if tbdata.loc[1,col] in table_dic.keys():
            tbdata.loc[1,col] += '(1)'
        table_dic[tbdata.loc[1,col]] = col_dic
    if tbdata.loc[1,0].startswith('初级规格'):
        table_dic = {tbdata.loc[0,0]:{tbdata.loc[1,0]:table_dic}}
    else:
        table_dic = {tbdata.loc[0,0]:table_dic}
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
    
    pro_intro_text = tree.xpath('.//div[@class="content c1"]//text()')
    pro_intro_text = ''.join([item.strip() for item in pro_intro_text])
    pro_intro['介绍信息'] = pro_intro_text
    pro_intro_imgtree = tree.xpath('.//div[@class="content c1"]//img')
    if pro_intro_imgtree != []:
        pro_intro['命名规则'] = []
        for img in pro_intro_imgtree:
            pro_intro['命名规则'].append(urljoin(page_url,img.xpath('./@src')[0]))

    pro_arg_text = tree.xpath('.//div[@class="content c2"]//text()')
    pro_arg_text = ''.join([item.strip() for item in pro_arg_text])
    pro_args['text'] = pro_arg_text
    pro_arg_imgtree = tree.xpath('.//div[@class="content c2"]//img')
    if pro_arg_imgtree != []:
        pro_args['img'] = []
        for img in pro_arg_imgtree:
            pro_args['img'].append(urljoin(page_url,img.xpath('./@src')[0]))
    try:
        tbdatas = pd.read_html(page_url)
        pro_args['table'] = parse_arg_table(tbdatas[0])
    except Exception as e:
        pass

    pro_dic = {'基本信息':pro_basic,'产品介绍':pro_intro,'产品参数':pro_args}
    return pro_dic

def ARC_Motor(headers,filename='ARC/Tube/voice_coil_motor.json'):
    final_dic = {}
    linear_url = 'https://www.hansmotor.com/products/10/c-10/'
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
    ARC_Motor(headers=headers,filename='弧形管形音圈电机.json')
