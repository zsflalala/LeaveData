import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin

def renew_table_coldupindex(tbdata):
    new_columns = []
    for col in tbdata.columns.values:
        if col[0][0:2] == col[1][0:2]:
            new_columns.append(col[1])
        else:
            new_columns.append(col[0]+'-'+col[1])
    tbdata.columns = new_columns
    
    rows = list(tbdata.index)
    last_col = 0
    for col in list(tbdata):
        if col.endswith('.1'):
            for row in rows:
                if str(tbdata.loc[row,col]) == 'nan':
                    continue
                if tbdata.loc[row,col] != tbdata.loc[row,last_col]:
                    tbdata.loc[row,last_col] += '-' +  str(tbdata.loc[row,col])
            tbdata = tbdata.drop(columns=col)
        last_col = col
    colunm_index = tbdata.columns.values.tolist()
    col_length = len(tbdata.columns.values.tolist())

    if 0 not in colunm_index:
        first_row = {}
        for i in range(col_length):
            first_row[i] = colunm_index[i]
            tbdata = tbdata.rename(columns={colunm_index[i]:i})
        dfhead = pd.DataFrame(first_row,index=[0])
        tbdata = dfhead._append(tbdata, ignore_index = True)
    return tbdata

def renew_table_colindex(tbdata):
    col_length = len(tbdata.columns.values.tolist())
    # 数据头索引不是 0 - 5 构成 重新创建
    col_index = tbdata.columns.values.tolist()
    if 0 not in col_index:
        first_row = {}
        for i in range(col_length):
            if isinstance(col_index[i],tuple):
                first_row[i] = col_index[i][0]
            else:
                first_row[i] = col_index[i]
            tbdata = tbdata.rename(columns={col_index[i]:i})
        dfhead = pd.DataFrame(first_row,index=[0])
        tbdata = dfhead._append(tbdata, ignore_index = True)
    return tbdata

def parse_arg_table(tbdata,startrow=1,startcol=1):
    table_dic = {}
    col_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    
    for row in range(startrow,row_length):
        row_dic = {}
        if str(tbdata.loc[row,0]) == 'nan':
            continue
        if tbdata.loc[row,0] not in table_dic.keys():
            table_dic[tbdata.loc[row,0]] = []
        for col in range(startcol,col_length):
            row_dic[tbdata.loc[0,col]] = str(tbdata.loc[row,col])
        table_dic[tbdata.loc[row,0]].append(row_dic)
    table_dic = {tbdata.loc[0,0]:table_dic}
    return table_dic

# 产品名称 产品类别 产品网址 产品图片 产品简介 资料下载-下载目录PDF 特征 规格选购 选购配件
def parse_intro(page_url,tree):
    pro_dic = {}
    pro_name = tree.xpath('.//div[@id="category"]/div[2]//text()')[0]
    pro_series = tree.xpath('.//div[@id="category"]/div[3]//text()')[0]
    pro_img = urljoin(page_url,tree.xpath('.//div[@id="category"]//div[@class="series"]//img/@src')[0])
    pro_intro = tree.xpath('.//div[@id="category"]//div[@class="txtbox"]//text()')
    pro_intro = ''.join([item.strip() for item in pro_intro])
    pro_download_tree = tree.xpath('.//div[@class="service_menu"]/p')

    pro_dic['产品名称'] = pro_name
    pro_dic['产品类别'] = pro_series
    pro_dic['产品网址'] = page_url
    pro_dic['产品图片'] = pro_img
    pro_dic['产品简介'] = pro_intro

    if pro_download_tree != []:
        pro_dic['资料下载'] = {}
        for p in pro_download_tree:
            p_url = urljoin(page_url,p.xpath('.//a/@href')[0])
            p_title = p.xpath('.//text()')
            p_title = ''.join([item.strip() for item in p_title])
            pro_dic['资料下载'][p_title] = p_url
    return pro_dic

def parse_feature(page_url,headers):
    pro_dic = {}
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_intro_dic = parse_intro(page_url,tree)
    pro_dic |= pro_intro_dic

    pro_dic['特征'] = {}
    all_text = tree.xpath('.//div[@class="detailbox"]//text()')
    all_text = ''.join([item.strip() for item in all_text])
    subtitle_list = []
    tabsubtitles_tree = tree.xpath('.//div[@class="detailbox"]//div[@class="tabsubtitle"]')
    if tabsubtitles_tree == []:
        tabsubtitles_tree = tree.xpath('.//div[@class="detailbox"]/p[@class="sv_finding"]')
    for subtitle in tabsubtitles_tree:
        subtitle = subtitle.xpath('.//text()')
        subtitle = ''.join([item.strip() for item in subtitle])
        subtitle_list.append(subtitle)

    if subtitle_list != []:
        split_text = all_text.split(subtitle_list[0],maxsplit=1)
        for i in range(1,len(subtitle_list)):
            split_list = split_text[-1].split(subtitle_list[i],maxsplit=1)
            del split_text[-1]
            split_text += split_list
        for i in range(1,len(split_text)):
            pro_dic['特征'][subtitle_list[i-1]] = split_text[i]

    pro_imgs = []
    pro_img_tree = tree.xpath('.//div[@class="detailbox"]//img')
    if pro_img_tree != []:
        for img in pro_img_tree:
            pro_imgs.append(urljoin(page_url,img.xpath('./@src')[0]))
        pro_dic['特征']['img'] = pro_imgs

    pro_movies = []
    pro_movie_tree = tree.xpath('.//video[@id="movie"]')
    if pro_movie_tree != []:
        for movie in pro_movie_tree:
            pro_movies.append(urljoin(page_url,movie.xpath('./source/@src')[0]))
        pro_dic['特征']['movie'] = pro_movies

    pro_hrefs = []
    pro_href_tree = tree.xpath('.//div[@class="detailbox"]//a')
    if pro_href_tree != []:
        for href in pro_href_tree:
            pro_hrefs.append(urljoin(page_url,href.xpath('./@href')[0]))
        pro_dic['特征']['其他产品链接'] = pro_hrefs
    
    return pro_dic

def parse_robot_NX_arg(page_url,headers):
    pro_dic = {}
    pro_dic['规格选购'] = {}
    page_url = page_url[:-2] + 'v/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@id="category"]/div[2]//text()')[0]
    if pro_name == '机器人控制器':
        pro_buy_text = tree.xpath('//*[@id="category"]/font/div[2]/span/font/text()[1]')[0]
        pro_dic['规格选购']['text'] = pro_buy_text
    elif pro_name == '免增益调整AC伺服电动机组合产品':
        pro_buy_text = tree.xpath('//*[@id="category"]/div[7]/b/font[2]/text()')[0]
        pro_dic['规格选购']['text'] = pro_buy_text
        pro_machine = []
        pro_machine_tree = tree.xpath('.//div[@class="detailbox"]//a')
        for machine in pro_machine_tree:
            pro_machine.append(urljoin(page_url,machine.xpath('./@href')[0]))
        pro_dic['规格选购']['机型链接'] = pro_machine
    tbdata = pd.read_html(page_url)[-1]
    pro_dic['规格选购']['table'] = parse_arg_table(renew_table_colindex(tbdata))
    return pro_dic

def parse_STEP_row_table(tbdata,startrow=1,startcol=1,rowkey=0):
    table_dic = {}
    col_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    
    # 处理行名
    for col in range(col_length):
        if tbdata.loc[0,col] == '电磁制动' and (tbdata.loc[1,col] == '有' or tbdata.loc[1,col] == '无'):
            tbdata.loc[1,col] = tbdata.loc[0,col] + tbdata.loc[1,col]

    for row in range(startrow,row_length):
        row_dic = {}
        if str(tbdata.loc[row,0]) == 'nan':
            continue
        if tbdata.loc[row,0] not in table_dic.keys():
            table_dic[tbdata.loc[row,0]] = []
        for col in range(startcol,col_length):
            row_dic[tbdata.loc[rowkey,col]] = str(tbdata.loc[row,col])
        table_dic[tbdata.loc[row,0]].append(row_dic)
    table_dic = {tbdata.loc[0,0]:table_dic}
    return table_dic

def parse_STEP_arg(page_url,headers):
    pro_dic = {}
    pro_dic['规格选购'] = {}
    page_url = page_url[:-2] + 'v/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    tbdatas = pd.read_html(page_url)

    pro_dic['规格选购']['品名阅读方法'] = urljoin(page_url,tree.xpath('//*[@id="category"]/div[5]/div/div/font/p[1]/font/a/@href')[0])
    
    for i in range(1,3):
        subtitle = tree.xpath(f'//*[@id="category"]/div[5]/div/font[2]/div[{i}]/text()')[0]
        subtitle_table = parse_STEP_row_table(tbdata=renew_table_coldupindex(tbdatas[i-1]))
        subtitle_link = []
        a_list = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/table[i]//a')
        for a in a_list:
            subtitle_link.append(urljoin(page_url,a.xpath('./@href')[0]))
        pro_dic['规格选购'][subtitle] = {'table':subtitle_table,'机型链接':subtitle_link}

    subtitle = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/div[3]/text()')[0]
    subtitle_text = tbdatas[2].loc[0,2]
    subtitle_table = parse_STEP_row_table(tbdata=renew_table_coldupindex(tbdatas[3]))
    subtitle_link = []
    a_list = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/table[4]//a')
    for a in a_list:
        subtitle_link.append(urljoin(page_url,a.xpath('./@href')[0]))
    pro_dic['规格选购'][subtitle] = {'text':subtitle_text,'table':subtitle_table,'机型链接':subtitle_link}

    subtitle = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/div[4]/text()')
    subtitle = ''.join([item.strip() for item in subtitle])
    subtitle_text = tbdatas[4].loc[0,2]
    tbdata = tbdatas[5]
    subtitle_table1 = parse_arg_table(renew_table_colindex(tbdata)) 
    tbdata = tbdatas[6]
    subtitle_table2 = parse_arg_table(renew_table_colindex(tbdata)) 
    tbdata = tbdatas[7]
    subtitle_table3 = parse_arg_table(renew_table_colindex(tbdata)) 
    subtitle_link = []
    for i in range(5,8):
        a_list = tree.xpath(f'//*[@id="category"]/div[5]/div/font[2]/table[{i}]//a')
        for a in a_list:
            subtitle_link.append(urljoin(page_url,a.xpath('./@href')[0]))
    pro_dic['规格选购'][subtitle] = {'text':subtitle_text,'table1':subtitle_table1,
                                 'table2':subtitle_table2,'table3':subtitle_table3,
                                 '机型链接':subtitle_link}
    
    subtitle = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/div[5]/text()')[0]
    subtitle_text = tbdatas[8].loc[0,2]
    subtitle_link = []
    a_list = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/table[9]//a')
    subtitle_link.append(urljoin(page_url,a_list[0].xpath('./@href')[0]))
    pro_dic['规格选购'][subtitle] = {'text':subtitle_text,'机型链接':subtitle_link}

    pro_dic['规格选购']['选购配件'] = []
    pro_accessories_title1 = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/div[7]/text()')[0]
    pro_accessories_title2 = tree.xpath('//*[@id="category"]/div[5]/div/font[2]/div[9]/text()')[0]
    subtable_title = []
    div_list = tree.xpath('.//div[@class="setting_sec01"]')
    for div in div_list:
        dt_list = div.xpath('./dl/dt')
        for dt in dt_list:
            subtable_title.append(dt.xpath('./a/text()')[0])
    title_dic1 = {pro_accessories_title1:[]}
    title_dic2 = {pro_accessories_title2:[]}
    for i in range(10,20):
        if i < 15:
            chose_dic = title_dic1
            accessories_title = pro_accessories_title1
        else:
            chose_dic = title_dic2
            accessories_title = pro_accessories_title2
        tbdata = tbdatas[i-1]
        table_dic = parse_arg_table(renew_table_colindex(tbdata))
        chose_dic[accessories_title].append({subtable_title[i-10]:table_dic})
    pro_dic['规格选购']['选购配件'].append(title_dic1)
    pro_dic['规格选购']['选购配件'].append(title_dic2)

    pro_dic['系统构成'] = {}
    page_url = page_url[:-2] + 's/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    subtitle = tree.xpath('//*[@id="category"]/font/div[4]/div[1]/text()')[0]
    subtitle_img = []
    for i in range(1,3):
        subtitle_img.append(urljoin(page_url,tree.xpath(f'//*[@id="category"]/font/div[4]/img[{i}]/@src')[0]))
    pro_dic['系统构成'][subtitle] = {'img':subtitle_img}
    subtitle = tree.xpath('//*[@id="category"]/font/div[4]/div[2]/text()')[0]
    subtitle_img = []
    for i in range(3,5):
        subtitle_img.append(urljoin(page_url,tree.xpath(f'//*[@id="category"]/font/div[4]/img[{i}]/@src')[0]))
    pro_dic['系统构成'][subtitle] = {'img':subtitle_img}
    return pro_dic

def parse_AZSTEP_arg(page_url,headers):
    pro_dic = {}
    pro_dic['规格选购'] = {}
    page_url = page_url[:-2] + 'v/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    tbdatas = pd.read_html(page_url)
    tbdata = tbdatas[0]
    table_dic = parse_arg_table(renew_table_colindex(tbdata))
    pro_dic['规格选购']['table'] = table_dic

    subtitle = tree.xpath('//*[@id="category"]//div[@class="tabsubtitle"]/text()')[0]
    subtitle_text = tree.xpath('//*[@id="category"]/font/div[2]/p//text()')
    subtitle_text = ''.join([item.strip() for item in subtitle_text])
    pro_dic['规格选购'][subtitle] = subtitle_text

    img_list = []
    img_tree = tree.xpath('.//div[@id="category"]//img')
    if img_tree != []:
        for img in img_tree:
            img_list.append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_dic['规格选购']['img'] = img_list

    link_list = []
    link_tree = tree.xpath('.//div[@class="detailbox"]//a')
    if link_tree != []:
        for link in link_tree:
            link_list.append(urljoin(page_url,link.xpath('./@href')[0]))
    pro_dic['规格选购']['其他产品链接'] = link_list

    sysconstruction = tree.xpath('.//a[@class="btn02"]')
    if sysconstruction != []:
        pro_dic['系统构成'] = {}
        page_url = page_url[:-2] + 's/'
        resp = requests.get(url=page_url,headers=headers)
        tree = etree.HTML(resp.text)
        
        subtitle_img = []
        img_tree = tree.xpath('.//div[@class="detailbox"]//img')
        if img_tree != []:
            for img in img_tree:
                subtitle_img.append(urljoin(page_url,img.xpath('./@src')[0]))
        pro_dic['系统构成']['img'] = subtitle_img

    return pro_dic

def parse_2_motor_arg(page_url,headers):
    pro_dic = {}
    pro_dic['规格选购'] = {}
    page_url = page_url[:-2] + 'v/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    tbdatas = pd.read_html(page_url)

    pro_dic['规格选购']['品名阅读方法'] = urljoin(page_url,tree.xpath('//*[@id="category"]/div[5]/div/div/font/p[1]/font/a/@href')[0])

    for i in range(1,6):
        tbdata = tbdatas[i-1]
        name = tree.xpath(f'//*[@id="a0{i}"]/text()')[0]
        table_dic = parse_arg_table(renew_table_colindex(tbdata))
        pro_dic['规格选购'][name] = table_dic
    
    pro_dic['规格选购']['选购配件'] = []
    div_list = tree.xpath('//*[@id="category"]/div[5]/font[2]/div[@class="setting_tit01"]')
    accessories_titles = []
    for div in div_list:
        title = div.xpath('./text()')[0]
        accessories_titles.append(title)
        pro_dic['规格选购']['选购配件'].append({title:[]})

    accessories_subtitles = []
    div_list = tree.xpath('//*[@id="category"]/div[5]/font[2]/div[@class="setting_sec01"]')
    for div in div_list:
        dt_list = div.xpath('./dl/dt')
        for dt in dt_list:
            accessories_subtitles.append(dt.xpath('./a/text()')[0])

    for i in range(5,24):
        tbdata = tbdatas[i]
        subtitle = accessories_subtitles[i-5]
        table_dic = parse_arg_table(renew_table_colindex(tbdata))
        if i <= 9:
            pro_dic['规格选购']['选购配件'][0][accessories_titles[0]].append({subtitle:table_dic})
        elif i <= 10:
            pro_dic['规格选购']['选购配件'][1][accessories_titles[1]].append({subtitle:table_dic})
        elif i <= 13:
            pro_dic['规格选购']['选购配件'][2][accessories_titles[2]].append({subtitle:table_dic})
        elif i <= 18:
            pro_dic['规格选购']['选购配件'][3][accessories_titles[3]].append({subtitle:table_dic})
        elif i <= 20:
            pro_dic['规格选购']['选购配件'][4][accessories_titles[4]].append({subtitle:table_dic})
        else:
            pro_dic['规格选购']['选购配件'][5][accessories_titles[5]].append({subtitle:table_dic})

    pro_dic['系统构成'] = {}
    page_url = page_url[:-2] + 's/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    
    subtitle_img = []
    img_tree = tree.xpath(f'//div[@class="detailbox"]//img')
    for img in img_tree:
        subtitle_img.append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_dic['系统构成']['img'] = subtitle_img
    return pro_dic

def parse_5_motor_arg(page_url,headers):
    pro_dic = {}
    pro_dic['规格选购'] = {}
    page_url = page_url[:-2] + 'v/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    tbdatas = pd.read_html(page_url)

    pro_dic['规格选购']['品名阅读方法'] = urljoin(page_url,tree.xpath('//*[@id="category"]/div[5]/div/div/font/b/font/p[1]/font/a/@href')[0])
    tbdata = tbdatas[0]
    table_dic = parse_arg_table(renew_table_colindex(tbdata))
    pro_dic['规格选购']['table'] = table_dic

    pro_dic['规格选购']['选购配件'] = []
    
    div_list = tree.xpath('//*[@id="category"]/div[5]/div/div/font/font[1]/div[@class="setting_tit01"]')
    accessories_titles = []
    for div in div_list:
        title = div.xpath('./text()')[0]
        accessories_titles.append(title)
        pro_dic['规格选购']['选购配件'].append({title:[]})

    accessories_subtitles = []
    div_list = tree.xpath('//*[@id="category"]/div[5]/div/div/font/font[1]/div[@class="setting_sec01"]')
    for div in div_list:
        dt_list = div.xpath('./dl/dt')
        for dt in dt_list:
            accessories_subtitles.append(dt.xpath('./a/text()')[0])

    for i in range(1,20):
        tbdata = tbdatas[i]
        subtitle = accessories_subtitles[i-1]
        table_dic = parse_arg_table(renew_table_colindex(tbdata))
        if i <= 5:
            pro_dic['规格选购']['选购配件'][0][accessories_titles[0]].append({subtitle:table_dic})
        elif i <= 6:
            pro_dic['规格选购']['选购配件'][1][accessories_titles[1]].append({subtitle:table_dic})
        elif i <= 9:
            pro_dic['规格选购']['选购配件'][2][accessories_titles[2]].append({subtitle:table_dic})
        elif i <= 14:
            pro_dic['规格选购']['选购配件'][3][accessories_titles[3]].append({subtitle:table_dic})
        elif i <= 16:
            pro_dic['规格选购']['选购配件'][4][accessories_titles[4]].append({subtitle:table_dic})
        else:
            pro_dic['规格选购']['选购配件'][5][accessories_titles[5]].append({subtitle:table_dic})


    pro_dic['系统构成'] = {}
    page_url = page_url[:-2] + 's/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    
    subtitle_img = []
    img_tree = tree.xpath(f'//div[@class="detailbox"]//img')
    for img in img_tree:
        subtitle_img.append(urljoin(page_url,img.xpath('./@src')[0]))
    pro_dic['系统构成']['img'] = subtitle_img
    return pro_dic

def parse_25_motor_arg(page_url,headers):
    pro_dic = {}
    pro_dic['规格选购'] = {}
    page_url = page_url[:-2] + 'v/'
    resp = requests.get(url=page_url,headers=headers)
    tree = etree.HTML(resp.text)
    tbdatas = pd.read_html(page_url)
    
    pro_dic['规格选购']['品名阅读方法'] = urljoin(page_url,tree.xpath('//*[@id="category"]/div[4]/font/div[2]/div/font/p/font/a/@href')[0]) 
    tbdata = tbdatas[0]
    table_dic = parse_arg_table(renew_table_colindex(tbdata))
    pro_dic['规格选购']['table'] = table_dic

    subtitle = tree.xpath('//*[@id="category"]//div[@class="tabsubtitle"]/text()')[0]
    subtitle_text = tree.xpath('//*[@id="category"]/div[4]/font/div[2]/div/font/font/text()')
    subtitle_text = ''.join([item.strip() for item in subtitle_text])
    pro_dic['规格选购'][subtitle] = subtitle_text

    link_list = []
    link_tree = tree.xpath('.//div[@class="detailbox"]//a')
    if link_tree != []:
        for link in link_tree:
            link_list.append(urljoin(page_url,link.xpath('./@href')[0]))
    del link_list[0]
    pro_dic['规格选购']['其他产品链接'] = link_list
    return pro_dic

def Oriental_Motor(headers,filename='oriental_motor.json'):
    final_dic = {}
    pro_urls = [
        'https://www.orientalmotor.com.cn/products/ct/mrc01_f/',
        'https://www.orientalmotor.com.cn/products/sv/tuningless_nx_f/',
        'https://www.orientalmotor.com.cn/products/st/astep_az_f/',
        'https://www.orientalmotor.com.cn/products/st/cvd_f/',
        'https://www.orientalmotor.com.cn/products/st/stepmotor_pkp2_f/',
        'https://www.orientalmotor.com.cn/products/st/stepmotor_pkp5_f/',
        'https://www.orientalmotor.com.cn/products/st/az_ethernetdriver_f/',
        'https://www.orientalmotor.com.cn/products/st/az_ethercatdriver_f/',
        'https://www.orientalmotor.com.cn/products/st/az_profinet_f/',
        'https://www.orientalmotor.com.cn/products/st/az_mini_f/'
    ]
    for url in pro_urls:
        tree = etree.HTML(requests.get(url=url,headers=headers).text)
        pro_name = tree.xpath('.//div[@id="category"]/div[2]//text()')[0]
        pro_dic = {}
        if pro_name == '免增益调整AC伺服电动机组合产品':
            pro_dic = parse_feature(url,tree)
            pro_dic |= parse_robot_NX_arg(url,headers=headers)
        elif pro_name == '机器人控制器':
            pro_dic = parse_feature(url,tree)
            pro_dic |= parse_robot_NX_arg(url,headers=headers)
        elif pro_name == '步进伺服混合控制系统αSTEP' and url.endswith('az_f/'):
            pro_name = tree.xpath('//*[@id="category"]/div[3]/p//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_dic = parse_feature(url,tree)
            pro_dic |= parse_STEP_arg(url,headers=headers)
        elif pro_name == '2相·5相步进步进电动机驱动器':
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_25_motor_arg(url,tree)
        elif pro_name == '2相步进电动机':
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_2_motor_arg(url,tree)
        elif pro_name == '5相步进电动机':
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_5_motor_arg(url,tree)
        elif pro_name == '步进伺服混合控制系统αSTEP' and url.endswith('ethernetdriver_f/'):
            pro_name = tree.xpath('//*[@id="category"]/div[3]/p//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_AZSTEP_arg(url,headers=headers)
        elif pro_name == '步进伺服混合控制系统αSTEP' and url.endswith('ethercatdriver_f/'):
            pro_name = tree.xpath('//*[@id="category"]/div[3]/p//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_AZSTEP_arg(url,headers=headers)
        elif pro_name == '步进伺服混合控制系统αSTEP' and url.endswith('profinet_f/'):
            pro_name = tree.xpath('//*[@id="category"]/div[3]/p//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_AZSTEP_arg(url,headers=headers)
        elif pro_name == '步进伺服混合控制系统αSTEP' and url.endswith('mini_f/'):
            pro_name = tree.xpath('//*[@id="category"]/div[3]/p//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_dic |= parse_feature(url,tree)
            pro_dic |= parse_AZSTEP_arg(url,headers=headers)
        final_dic[pro_name] = pro_dic

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")
    return final_dic

if __name__ == "__main__":
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    Oriental_Motor(headers=headers,filename='东方马达.json')
