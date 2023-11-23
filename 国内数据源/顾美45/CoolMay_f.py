import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin

# 保存正常类型表格
def save_normal_table(tbdata,tree=None):
    pro_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())

    # pro_dic[tbdata.loc[0][0]] = list(set([tbdata.loc[0,i] for i in range(1,colunm_length)]))
    row = 1 
    img_id = 1
    for col in range(1,colunm_length):
        pro_dic[tbdata.loc[0][col]] = {}
        while row < row_length:
            # 含有产品图片的表格
            if img_id < 5 and tbdata.loc[row][0] == '产品图片':
                img_zheng = tree.xpath(f'//*[@id="tabs_pro"]/div[2]/samp[2]/table[1]/tbody/tr[2]/td[{img_id+1}]/a/img/@src')[0]
                img_fan = tree.xpath(f'//*[@id="tabs_pro"]/div[2]/samp[2]/table[1]/tbody/tr[3]/td[{img_id}]/a/img/@src')[0]
                img_id += 1
                pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = img_zheng + ';' + img_fan
                row += 1
            # 运动控制和系统中的特殊存在
            elif tbdata.loc[row][0] == '位置控制':
                shuru = []
                chilunbi = []
                while row < row_length:
                    shuru.append(tbdata.loc[row][colunm_length-1])
                    chilunbi.append(tbdata.loc[row][colunm_length-1])
                    row += 1
                row -= 1
                pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = {'输入方式':shuru,'输入电子齿轮比':chilunbi}
            elif tbdata.loc[row][0] == tbdata.loc[row][colunm_length-1]:
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


# IoT
# 表格 (1个)
def save_iot_table(tbdata,url,tree):
    pro_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())

    # 数据头索引不是 0 - 5 构成 重新创建
    first_row = {}
    colunm_index = tbdata.columns.values.tolist()
    for i in range(colunm_length):
        first_row[i] = colunm_index[i]
        tbdata = tbdata.rename(columns={colunm_index[i]:i})
    dfhead = pd.DataFrame(first_row,index=[0])
    tbdata = dfhead._append(tbdata, ignore_index = True)
    row_length = len(tbdata._stat_axis.values.tolist())

    # head_key = [tbdata.loc[0,i] for i in range(2,colunm_length)]
    # del head_key[head_key.index('/')]
    # pro_dic[tbdata.loc[0][0]] = list(set(head_key))

    row = 1 
    img_id = 1
    for col in range(2,colunm_length):
        if tbdata.loc[0][col] == '/':
            continue
        pro_dic[tbdata.loc[0][col]] = {}
        while row < row_length:
            # 含有产品图片的表格
            if img_id < 3 and tbdata.loc[row][0] == '产  品  图  片':
                img_zheng = tree.xpath(f'//*[@id="tabs_pro"]/div[2]/samp[1]/table/tbody/tr[2]/td[{img_id}]//img/@src')[0]
                img_fan = tree.xpath(f'//*[@id="tabs_pro"]/div[2]/samp[1]/table/tbody/tr[3]/td[{img_id}]//img/@src')[0]
                img_zheng = urljoin(url,img_zheng)
                img_fan = urljoin(url,img_fan)
                img_id += 1
                pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = {"正面":img_zheng,"反面":img_fan}
                row += 1
            elif img_id < 6 and tbdata.loc[row][0] == '产  品  图  片':
                if img_id == 3:
                    img_id += 1
                img_zheng = tree.xpath(f'//*[@id="tabs_pro"]/div[2]/samp[1]/table/tbody/tr[2]/td[{img_id}]/a/@href')[0]
                img_fan = tree.xpath(f'//*[@id="tabs_pro"]/div[2]/samp[1]/table/tbody/tr[3]/td[{img_id}]/a/@href')[0]
                img_id += 1
                pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = {"正面":img_zheng,"反面":img_fan}
                row += 1
            else:
                pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = tbdata.loc[row][col]
            row += 1
        row = 1
    pro_dic = {tbdata.loc[0][0]:pro_dic}
    return pro_dic

def IOT_spider(headers,filename='iot.json'):
    iot_url = 'http://www.coolmay.com/ProductDetail.aspx?ColumnId=225&ArticleId=1645&Language=34&Terminal=41'
    tbdata = pd.read_html(iot_url,encoding='utf-8')[0]
    resp = requests.get(url=iot_url,headers=headers)
    tree = etree.HTML(resp.text)
    final_dic = {}
    
    product_name = tree.xpath('.//div[@class="Prod_xq_t1_right_t"]/span/text()')[0]
    pro_dic = save_iot_table(tbdata=tbdata,url=iot_url,tree=tree)
    product_pic_url = urljoin(iot_url,tree.xpath('.//div[@class="Prod_xq_t1_left"]/img/@src')[0])

    final_dic[product_name] = {}
    final_dic[product_name]['产品名称'] = product_name
    final_dic[product_name]['产品图片'] = product_pic_url
    final_dic[product_name]['产品特点'] = ""
    final_dic[product_name]['产品参数'] = pro_dic
    final_dic[product_name]['安装尺寸'] = ""


    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


# 工业开关电源
def switch_power_spider(headers,filename='switch_power.json'):
    swich_url = 'http://www.coolmay.com/PicList.aspx?ColumnId=213&Language=34&Terminal=41'
    resp = requests.get(url=swich_url,headers=headers)
    tree = etree.HTML(resp.text)
    li_lists = tree.xpath('.//div[@class="Pro_list"]/ul/li')
    final_dic = {}
    product_names,product_urls = [],[]
    for li in li_lists:
        product_name = li.xpath('./div[2]/a/text()')[0].strip()
        product_url = urljoin(swich_url,li.xpath('./div[2]/a/@href')[0])
        product_names.append(product_name)
        product_urls.append(product_url)
    
    for index in range(0,len(product_urls)):
        final_dic[product_names[index]] = {}
        tree = etree.HTML(requests.get(url=product_urls[index],headers=headers).text)

        product_feature = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
        product_feature = ''.join([item.replace('\xa0','').strip() for item in product_feature if item.strip()])
        product_args = urljoin(swich_url,tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[2]/img/@src')[0])
        product_pic_url = urljoin(swich_url,tree.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/div/div[1]/div[1]/img/@src')[0])

        install_dic = {}
        size = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p[1]/span[1]/text()')[0].strip()
        size_content = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p[1]/span[2]/text()')[0].strip()
        size_img = urljoin(swich_url,tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p//img/@src')[0])
        install_dic['text'] = size + size_content
        install_dic['img'] = size_img

        final_dic[product_names[index]]['产品名称'] = product_names[index]
        final_dic[product_names[index]]['产品图片'] = product_pic_url
        final_dic[product_names[index]]['产品特点'] = product_feature
        final_dic[product_names[index]]['产品参数'] = product_args
        final_dic[product_names[index]]['安装尺寸'] = install_dic
        
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


# 传感器
def save_sensor_table(tbdata):
    pro_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())
    col = 0

    # 找型号属性对应的最大索引
    for i in range(colunm_length):
        if tbdata.loc[0][col] == tbdata.loc[0][col+1]:
            col += 1
        else:
            col += 1
            break
    child_col = col - 1
    duplicate = 1
    # pro_dic[tbdata.loc[0][0]] = list(set([tbdata.loc[0,i] for i in range(col,colunm_length)]))

    while col < colunm_length:
        if tbdata.loc[0][col] not in pro_dic.keys():
            pro_dic[tbdata.loc[0][col]] = {}
            duplicate = 1
        else:
            tbdata.loc[0][col] = tbdata.loc[0][col] + f'_({duplicate})'
            pro_dic[tbdata.loc[0][col]] = {}
            duplicate += 1
        row = 1 
        while row < row_length:
            if row + 1 < row_length and tbdata.loc[row][0] == tbdata.loc[row+1][0]:
                end_row = row + 1
                while end_row < row_length - 1 and tbdata.loc[end_row][0] == tbdata.loc[end_row+1][0]:
                    end_row += 1
                child_dic,child_dic_temp = {},{}
                while row <= end_row:
                    if child_col == 1:
                        # tbdata.loc[row][col] 是数据  tbdata.loc[row][child_col]是字段
                        child_dic_temp[tbdata.loc[row][child_col]] = tbdata.loc[row][col]
                    elif child_col == 2:
                        child_dic_temp[tbdata.loc[row][child_col]] = tbdata.loc[row][col]
                        child_dic[tbdata.loc[row][child_col-1]] = child_dic_temp
                    row += 1
                row -= 1
                if child_col == 1:
                    if not tbdata.loc[row][child_col-1] in pro_dic[tbdata.loc[0][col]].keys():
                        pro_dic[tbdata.loc[0][col]][tbdata.loc[row][child_col-1]] = child_dic_temp
                    else:
                        pro_dic[tbdata.loc[0][col]][tbdata.loc[row][child_col-1]] += ";" + child_dic_temp
                elif child_col == 2:
                    if not tbdata.loc[row-1][0] in pro_dic[tbdata.loc[0][col]].keys():
                        pro_dic[tbdata.loc[0][col]][tbdata.loc[row-1][0]] = child_dic
                    else:
                        pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = ';' +  child_dic
                
            else:
                if not tbdata.loc[row][0] in pro_dic[tbdata.loc[0][col]].keys():
                    pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] = tbdata.loc[row][col]
                else:
                    pro_dic[tbdata.loc[0][col]][tbdata.loc[row][0]] += ';' + tbdata.loc[row][col]
            row += 1
        col += 1
    pro_dic = {tbdata.loc[0][0]:pro_dic}
    return pro_dic

def Sensor_spider(headers,filename='sensor.json'):
    sensor_urls = [
        'http://www.coolmay.com/PicList.aspx?ColumnId=227&Language=34&Terminal=41&page=1',
        'http://www.coolmay.com/PicList.aspx?ColumnId=227&Language=34&Terminal=41&page=2'
    ]
    product_urls,product_names = [],[]
    final_dic = {}
    for sensor_url in sensor_urls:
        resp = requests.get(url=sensor_url,headers=headers)
        tree = etree.HTML(resp.text)
        li_lists = tree.xpath('.//div[@class="Pro_list"]/ul/li')
        for li in li_lists:
            product_name = li.xpath('./div[2]/a/text()')[0].strip()
            child_url = urljoin(sensor_url,li.xpath('./div[2]/a/@href')[0])
            product_names.append(product_name)
            product_urls.append(child_url)
    

    for index in range(len(product_urls)):
        final_dic[product_names[index]] = {}
        tree = etree.HTML(requests.get(url=product_urls[index],headers=headers).text)
        tbdatas = pd.read_html(product_urls[index],encoding='utf-8')
        for tbdata in tbdatas:
            row_length = len(tbdata._stat_axis.values.tolist())
            if row_length < 8:
                continue
            if tbdata.loc[0][0] == tbdata.loc[0][1]:
                pro_dic = save_sensor_table(tbdata=tbdata)
            else:
                pro_dic = save_normal_table(tbdata=tbdata)
        
        product_pic_url = urljoin(product_urls[index],tree.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/div/div[1]/div[1]/img/@src')[0])
        product_feature = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
        product_feature = ''.join([item.replace('\xa0','').strip() for item in product_feature if item.strip()])
        product_feature_imgs = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/table/tbody/tr//img/@src')
        product_feature_img = ""
        if len(product_feature_imgs):
            for img in product_feature_imgs:
                product_feature_img += urljoin(sensor_urls[0],img) + ';'
        product_feature = product_feature_img + product_feature

        install_dic = {}
        install_text = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]//text()')
        install_text = ''.join([item.replace('\xa0','').strip() for item in install_text if item.strip()])
        install_dic['text'] = install_text
        install_imgsrcs = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p//img/@src')
        install_img = ''
        if len(install_imgsrcs):
            for imgsrc in install_imgsrcs:
                install_img += urljoin(product_urls[index],imgsrc) + ';'
        install_dic['img'] = install_img

        final_dic[product_names[index]]['产品名称'] = product_names[index]
        final_dic[product_names[index]]['产品图片'] = product_pic_url
        final_dic[product_names[index]]['产品特点'] = product_feature
        final_dic[product_names[index]]['产品参数'] = pro_dic
        final_dic[product_names[index]]['安装尺寸'] = install_dic
        
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


# 变频器
def frequency_converter(headers,filename='frequence.json'):
    fre_url = 'http://www.coolmay.com/ProductDetail.aspx?ColumnId=168&ArticleId=1429&Language=34&Terminal=41'
    tree = etree.HTML(requests.get(url=fre_url,headers=headers).text)

    product_name = tree.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/div/div[1]/div[2]/div[1]/span/text()')[0]
    product_pic_url = urljoin(fre_url,tree.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/div/div[1]/div[1]/img/@src')[0])
    product_feature = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    product_feature = ''.join([item.replace('\xa0','').strip() for item in product_feature if item.strip()])
    product_feature_img = urljoin(fre_url,tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[24]/img/@src')[0])
    product_feature += ';' + product_feature_img
    product_arg = urljoin(fre_url,tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[2]/img/@src')[0])
    
    install_dic = {}
    install_dic['text'] = ''
    install_dic['img'] = ''

    final_dic = {}
    final_dic[product_name] = {}

    final_dic[product_name]['产品名称'] = product_name
    final_dic[product_name]['产品图片'] = product_pic_url
    final_dic[product_name]['产品特点'] = product_feature
    final_dic[product_name]['产品参数'] = product_arg
    final_dic[product_name]['安装尺寸'] = install_dic
        
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


# 运动控制和系统
def run_control_system(headers,filename='run_control_system.json'):
    run_control_url = 'http://www.coolmay.com/PicList.aspx?ColumnId=171&Language=34&Terminal=41'
    resp = requests.get(url=run_control_url,headers=headers)
    tree = etree.HTML(resp.text)
    final_dic = {}
    li_lists = tree.xpath('.//ul[@class="wrapfix"]/li')
    for li in li_lists:
        product_name = li.xpath('./div[2]/a/text()')[0].strip()
        final_dic[product_name] = {}
        product_url = urljoin(run_control_url,li.xpath('./div[2]/a/@href')[0])
        tree = etree.HTML(requests.get(url=product_url,headers=headers).text)
        
        tbdataframe = pd.read_html(product_url,encoding='utf-8')[0]
        product_dic = save_normal_table(tbdata=tbdataframe)
        product_pic_url = urljoin(product_url,tree.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/div/div[1]/div[1]/img/@src')[0])
        product_feature = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
        product_feature = ''.join([item.replace('\xa0','').strip() for item in product_feature if item.strip()])

        install_dic = {}
        install_dic['text'] = ''
        install_img = urljoin(run_control_url,tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]//img/@src')[0])
        install_dic['img'] = install_img

        final_dic[product_name]['产品名称'] = product_name
        final_dic[product_name]['产品图片'] = product_pic_url
        final_dic[product_name]['产品特点'] = product_feature
        final_dic[product_name]['产品参数'] = product_dic
        final_dic[product_name]['安装尺寸'] = install_dic

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    IOT_spider(headers=headers,filename='IoT物联网模块.json')
    switch_power_spider(headers=headers,filename='工业开关电源模块.json')
    Sensor_spider(headers=headers,filename='传感器模块.json')
    frequency_converter(headers=headers,filename='变频器模块.json')
    run_control_system(headers=headers,filename='运动控制和系统模块.json')

    