import numpy as np
import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin

def get_name_intro(url,pro_dic,tree):
    pro_name = tree.xpath('/html/body/div[4]/div[4]/div[2]/div[2]/h2/text()')[0]
    try:
        pro_intro = tree.xpath('/html/body/div[4]/div[4]/div[2]/div[2]/p[1]/text()')[0]
    except:
        pro_intro = ''
    pro_intro2 = tree.xpath('/html/body/div[4]/div[4]/div[2]/div[2]/div//text()')
    pro_intro2 = ''.join([item.strip() for item in pro_intro2 if item.strip()])
    pro_intro += pro_intro2
    pro_img = urljoin(url,tree.xpath('.//div[@class="picScrollbox xcd"]//img/@src')[0])
    pro_dic['产品名称'] = pro_name
    pro_dic['产品图片'] = pro_img
    pro_dic['产品介绍'] = pro_intro
    return pro_dic

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
            chosedic[dif_col[0]][dif_col[1]] = dif_col[2]
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

def parse_row_table(tbdata,startrow=1,startcol=1):
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

def parse_A3S_table2(tbdata):
    table_dic = {}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())
    keys = tbdata.loc[:,0]
    row_dif = list(dict.fromkeys(keys))

    # 以第0列为主键
    for rowkey in row_dif:
        table_dic[rowkey] = []
    for col in range(3,col_length):
        tbdata.loc[1,col] = tbdata.loc[0,col] + tbdata.loc[1,col]
    for row in range(2,row_length):
        row_dic = {}
        for col in range(2,col_length):
            row_dic[tbdata.loc[1,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[row,0]].append(row_dic)
    return table_dic

def get_A3S_args(page_url,pro_name):
    args = {}
    tbdata = pd.read_html(page_url)
    if pro_name == 'A3N网络型伺服驱动器':
        tbdata = tbdata[0]
        args = parse_col_table(tbdata)
    elif pro_name == 'A3S标准型伺服驱动器':
        assert len(tbdata) == 2
        tbdata0 = tbdata[0]
        args = args | parse_col_table(tbdata0)
        tbdata1 = tbdata[1]
        args = args | parse_A3S_table2(tbdata1)
    else:
        assert len(tbdata) == 5
        for i in range(0,3):
            tb = tbdata[i]
            args = args | parse_col_table(tb)
        for i in range(3,5):
            tb = tbdata[i]
            args = args | parse_row_table(tb)
    return args

def A3S_drive(headers):
    pro_dic = {}
    urls =[
        'https://www.co-trust.com/Products/Motion/ServoDriver/A3S/Product_241.html',
        'https://www.co-trust.com/Products/Motion/ServoDriver/A3N/Product_242.html',
        'https://www.co-trust.com/Products/Motion/ServoDriver/A4S/Product_279.html',
        'https://www.co-trust.com/Products/Motion/ServoDriver/A4N/Product_280.html'
    ]
    for url in urls:
        temp_dic = {}
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)

        temp_dic = get_name_intro(url,temp_dic,tree)
        basic = tree.xpath('/html/body/div[4]/div[5]/div/dl[1]/dd//text()')
        basic = ''.join([item.strip() for item in basic])

        args = get_A3S_args(url,temp_dic['产品名称'])
        application = ""
        install_specifications = []
        img_list = tree.xpath('/html/body/div[4]/div[5]/div/dl[4]/dd//img')
        for img in img_list:
            install_specifications.append(urljoin(url,img.xpath('./@src')[0]))
        sample = ''

        temp_info = {'概览':basic,'技术参数':args,'典型应用':application,'安装规格':install_specifications,'样本/手册/软件':sample}
        temp_dic['产品信息'] = temp_info
        pro_dic[temp_dic['产品名称']] = temp_dic
    return  pro_dic

def CPU226H_run_controller(url,headers):
    pro_dic = {}
    temp_dic = {}
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    temp_dic = get_name_intro(url,temp_dic,tree)

    tbdata = pd.read_html(url)
    basic = parse_row_table(tbdata[0],startrow=2)

    args = parse_col_table(tbdata[1])
    args_note = tree.xpath('/html/body/div[4]/div[5]/div/dl[2]/dd/p//text()')
    args_note = ''.join([item.strip() for item in args_note])
    args |= {'备注':args_note}
    application = ""
    install_specifications = tree.xpath('/html/body/div[4]/div[5]/div/dl[4]//img/@src')[0]
    sample = ''

    temp_info = {'概览':basic,'技术参数':args,'典型应用':application,'安装规格':install_specifications,'样本/手册/软件':sample}
    temp_dic['产品信息'] = temp_info
    pro_dic[temp_dic['产品名称']] = temp_dic
    return  pro_dic

def save_CTH300_table2(tbdata):
    pro_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    row = 1 
    start_col = 1
    for col in range(1,colunm_length-1):
        if tbdata.loc[0,col] != tbdata.loc[0,col+1]:
            start_col = col + 1
            break
    for col in range(start_col,colunm_length):
        pro_dic[tbdata.loc[0][col]] = {}
        while row < row_length:
            if tbdata.loc[row][0] == tbdata.loc[row][colunm_length-1]:
                key_name = tbdata.loc[row][0]
                value_dic = {}
                row += 1
                while row < row_length and tbdata.loc[row][0] != tbdata.loc[row][colunm_length-1]:
                    if not tbdata.loc[row][0] in value_dic.keys():
                        value_dic[tbdata.loc[row][0]] = tbdata.loc[row][col]
                    else:
                        value_dic[tbdata.loc[row][0]] += ';' + tbdata.loc[row][col]
                    row += 1
                pro_dic[tbdata.loc[0][col]][key_name] = value_dic
                row -= 1
            else:
                if not tbdata.loc[row][0] in pro_dic[tbdata.loc[0][col]].keys():
                    pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = tbdata.loc[row][col]
                else:
                    pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] += ';' + tbdata.loc[row][col]
            row += 1
        row = 0
    pro_dic = {tbdata.loc[0][0]:pro_dic}
    return pro_dic

def save_sample_table(url,tbdata):
    table_dic = {tbdata.loc[0][0]:{}}
    row_length = len(tbdata._stat_axis.values.tolist())
    col_length = len(tbdata.columns.values.tolist())
    keys = tbdata.loc[1:,0]
    row_dif = list(dict.fromkeys(keys))

    trid = 2
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)

    # 以第0列为主键
    for rowkey in row_dif:
        table_dic[tbdata.loc[0][0]][rowkey] = []
    for row in range(1,row_length):
        row_dic = {}
        for col in range(1,col_length):
            if tbdata.loc[0,col] == '下载':
                
                row_dic[tbdata.loc[0,col]] = tree.xpath(f'//*[@id="xcdown"]/dd//table/tbody/tr[{trid}]//a/@href')[0]
                trid += 1
            else:
                row_dic[tbdata.loc[0,col]] = tbdata.loc[row,col]
        table_dic[tbdata.loc[0][0]][tbdata.loc[row,0]].append(row_dic)
    return table_dic

def CTH300_run_ctroller(url,headers):
    pro_dic = {}
    temp_dic = {}
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    pro_name = tree.xpath('/html/body/div[4]/div[4]/div[2]/div[2]/h2/text()')[0]
    pro_intro = tree.xpath('/html/body/div[4]/div[4]/div[2]/div[2]/div//text()')
    pro_intro = ''.join([item.strip() for item in pro_intro])
    temp_dic['产品名称'] = pro_name
    temp_dic['产品介绍'] = pro_intro

    tbdata = pd.read_html(url)
    basic = parse_row_table(tbdata[0])

    args = save_CTH300_table2(tbdata[1])
    application = {}
    application['text'] = tree.xpath('/html/body/div[4]/div[5]/div/dl[3]/dd//text()')
    application['text'] = ''.join([item.strip() for item in application['text']])
    application['img'] = tree.xpath('//dl[@class="xcprodetail-list"]//img/@src')[0]
    install_specifications = tree.xpath('/html/body/div[4]/div[5]/div/dl[4]//img/@src')[0]
    sample = save_sample_table(url,tbdata[-1])

    temp_info = {'概览':basic,'技术参数':args,'典型应用':application,'安装规格':install_specifications,'样本/手册/软件':sample}
    temp_dic['产品信息'] = temp_info
    pro_dic[temp_dic['产品名称']] = temp_dic
    return  pro_dic

def Run_Controller(headers):
    pro_dic = {}
    urls =[
        'https://www.co-trust.com/Products/Motion/Motion/CTH300-C/Product_178.html',
        'https://www.co-trust.com/Products/Motion/Motion/CPU226H/Product_180.html',
    ]
    pro_dic |= CTH300_run_ctroller(urls[0],headers)
    pro_dic |= CPU226H_run_controller(urls[1],headers)
    return  pro_dic

def M_motor(headers):
    pro_dic = {}
    temp_dic = {}
    url = 'https://www.co-trust.com/Products/Motion/ServoMotor/Mseries/Product_185.html'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    temp_dic = get_name_intro(url,temp_dic,tree)

    basic = urljoin(url,tree.xpath('/html/body/div[4]/div[5]/div/dl[1]/dd/p/img/@src')[0])
    args = []
    img_list = tree.xpath('/html/body/div[4]/div[5]/div/dl[2]/dd//img')
    for img in img_list:
        args.append(urljoin(url,img.xpath('./@src')[0]))
    application = ""
    install_specifications = ''
    sample = ''
    pro_info = {'概览':basic,'技术参数':args,'典型应用':application,'安装规格':install_specifications,'样本/手册/软件':sample}
    temp_dic['产品信息'] = pro_info
    pro_dic[temp_dic['产品名称']] = temp_dic
    return pro_dic

def CTH200_PLC_shuzi(headers):
    pro_dic = {}
    temp_dic = {}
    pro_urls = []
    url = 'https://www.co-trust.com/Products/Programmable/CTH200/Digital/index.html'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('.//ul[@class="product-list"]/li')
    for li in li_list:
        pro_urls.append(urljoin(url,li.xpath('.//a/@href')[0])) 
    for i in range(len(pro_urls)):
        url = pro_urls[i]
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        temp_dic = get_name_intro(url,temp_dic,tree)
        tbdata = pd.read_html(url)
        basic = parse_row_table(tbdata[0])
        args = tree.xpath('/html/body/div[4]/div[5]/div/dl[2]//img/@src')[0]

        application = ""
        install_specifications = []
        img_list = tree.xpath('/html/body/div[4]/div[5]/div/dl[4]/dd/p')
        for img in img_list:
            install_specifications.append(img.xpath('.//img/@src')[0])
        sample = save_sample_table(url,tbdata[-1])
        pro_info = {'概览':basic,'技术参数':args,'典型应用':application,'安装规格':install_specifications,'样本/手册/软件':sample}
        temp_dic['产品信息'] = pro_info
        pro_dic[temp_dic['产品名称']] = temp_dic
    return pro_dic
    
def Programmable_controller(headers):
    final_dic = {}
    all_url = [
        'https://www.co-trust.com/Products/Programmable/CTH200/desc.html',
        'https://www.co-trust.com/Products/Programmable/CTH300/desc.html',
        'https://www.co-trust.com/Products/Programmable/CTMC/desc.html',
        'https://www.co-trust.com/Products/Programmable/CTSC-200/desc.html',  # 61
        'https://www.co-trust.com/Products/Programmable/CTSC-100/desc.html',
        'https://www.co-trust.com/Products/Programmable/Distributed/desc.html',
    ]
    for url in all_url:
        pro_dic = {}
        urls = []       # 产品种类页url
        urls_title = [] # 产品种类名称

        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        pro_series = tree.xpath('.//div[@class="commonweb clearfix  hidden-xs visible-md"]/h2/text()')[0]
        pro_desc = tree.xpath('.//div[@class="commonweb contentbox"]//text()')
        pro_desc = ''.join([item.strip() for item in pro_desc])
        pro_desc_img = []
        pro_desc_img_tree = tree.xpath('.//div[@class="commonweb contentbox"]//img')
        if pro_desc_img_tree != []:
            for img in pro_desc_img_tree:
                pro_desc_img.append(urljoin(url,img.xpath('./@src')[0]))
        pro_dic['概述'] = {'产品系列':pro_series,'系列概述':pro_desc,'系列图片':pro_desc_img} 

        a_list = tree.xpath('.//p[@class=" hidden-xs visible-md clearfix"]/a')[1:]
        for a in a_list:
            urls.append(urljoin(url,a.xpath('./@href')[0]))
            urls_title.append(a.xpath('./text()')[0])

        count = 0
        # 模块页
        for i in range(len(urls)):
            pro_urls = []   # 产品详情页url
            title = urls_title[i]
            pro_dic[title] = {}

            url = urls[i]
            resp = requests.get(url=url,headers=headers)
            resp.encoding = 'utf-8'
            tree = etree.HTML(resp.text)
            li_list = tree.xpath('.//ul[@class="product-list"]/li')
            for li in li_list:
                pro_urls.append(urljoin(url,li.xpath('.//a/@href')[0])) 

            # 产品模块页
            for j in range(len(pro_urls)):
                temp_dic = {}
                url = pro_urls[j]
                resp = requests.get(url=url,headers=headers)
                resp.encoding = 'utf-8'
                tree = etree.HTML(resp.text)
                temp_dic = get_name_intro(url,temp_dic,tree)
                try:
                    tbdata = pd.read_html(url)
                except:
                    tbdata = []
                
                basic = {}
                basic['text'] = tree.xpath('/html/body/div[4]/div[5]/div/dl[1]/dd/p//text()')
                basic['text'] = ''.join([item.strip() for item in basic['text']])
                basic_table_tree = tree.xpath('/html/body/div[4]/div[5]/div/dl[1]/dd/table')
                basic_img_tree = tree.xpath('/html/body/div[4]/div[5]/div/dl[1]/dd//img') 
                if basic_table_tree != []:
                    basic['table'] = parse_row_table(tbdata[0])
                elif basic_img_tree != []:
                    basic['img'] = urljoin(url,basic_img_tree[0].xpath('./@src')[0])
                
                args = []
                img_list = tree.xpath('/html/body/div[4]/div[5]/div/dl[2]/dd//img')
                if img_list != []:
                    for img in img_list:
                        args.append(urljoin(url,img.xpath('./@src')[0]))
                else:
                    if basic_table_tree == []:
                        args_table = tbdata[0]
                    else:
                        args_table = tbdata[1]
                    if temp_dic['产品名称'] == 'RS485通信扩展板':
                        args = parse_col_table(args_table,startrow=1)
                        args_table.to_csv('temp.csv',mode='w',encoding='utf-8',index=True,header=True)
                    else:
                        args = parse_col_table(args_table)
                    
                img_tree = tree.xpath('/html/body/div[4]/div[5]/div/dl[3]/dd//img')
                if img_tree != []:
                    application = img_tree[0].xpath('./@src')[0]
                else:
                    application = ""

                install_specifications = []
                img_list = tree.xpath('/html/body/div[4]/div[5]/div/dl[4]/dd/p')
                for img in img_list:
                    if img.xpath('.//img/@src') != []:
                        install_specifications.append(urljoin(url,img.xpath('.//img/@src')[0]))
                
                sample = ''
                sample_table_tree = tree.xpath('//*[@id="xcdown"]/dd/div/table')
                if sample_table_tree != []:
                    sample = save_sample_table(url,tbdata[-1])

                pro_info = {'概览':basic,'技术参数':args,'典型应用':application,'安装规格':install_specifications,'样本/手册/软件':sample}
                temp_dic['产品信息'] = pro_info
                pro_dic[title][temp_dic['产品名称']] = temp_dic
                count += 1
            print(f'已完成{pro_series}系列-->>{title}模块数据爬取,共{count}条数据')
        print(f'{count}条数据已爬取完成')
        final_dic[pro_series] = pro_dic
    return final_dic

def COTRUST(headers,filename='cotrust.json'):
    final_dic = {}
    cot_url = 'https://www.hansmotor.com/products/5/c-5/'
    resp = requests.get(cot_url,headers=headers)
    if resp.status_code != 200:
        print('状态码: ',resp.status_code)
        return None
    tree = etree.HTML(resp.text)
    
    pro_dic = M_motor(headers=headers)
    final_dic['电机'] = pro_dic
    pro_dic = A3S_drive(headers=headers)
    final_dic['驱动器'] = pro_dic
    pro_dic = Run_Controller(headers=headers)
    final_dic['运动控制器'] = pro_dic
    pro_dic = Programmable_controller(headers=headers)
    final_dic['可编程控制器'] = pro_dic
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")

if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    COTRUST(headers=headers,filename='合信技术.json')

