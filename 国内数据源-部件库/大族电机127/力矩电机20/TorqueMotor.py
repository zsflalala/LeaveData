import requests
import re
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


# 解析表格
def parse_table(tbdata,kind):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())

    if kind == 1:
        row = 2
        # 处理最左侧列名
        for i in range(2,row_length):
            tbdata.loc[i][0] += f" {tbdata.loc[1][1]}: {tbdata.loc[i][1]} ; {tbdata.loc[1][2]}: {tbdata.loc[i][2]}"

        for col in range(3,colunm_length):
            table_dic[tbdata.loc[1][col]] = {}
            while row < row_length:
                table_dic[tbdata.loc[1][col]][tbdata.loc[row][0]] = tbdata.loc[row][col]
                row += 1
            row = 2
        table_dic = {tbdata.loc[0][0]:table_dic}
    elif kind == 2:
        row = 1
        while row < row_length:
            col = 1
            table_dic[tbdata.loc[row][0]] = {}
            while col < colunm_length:
                table_dic[tbdata.loc[row][0]][tbdata.loc[0][col]] = tbdata.loc[row][col]
                col += 1
            row += 1
        table_dic = {tbdata.loc[0][0]:table_dic}

    return table_dic

# 产品信息
def parse_basic(page_url,tree):
    pro_name = tree.xpath('.//div[@class="base-info"]/div[1]/text()')[0].strip()
    pro_feature = tree.xpath('.//div[@class="base-info"]/div[3]//text()')
    pro_feature = ''.join([item.replace('\xa0','').strip() for item in pro_feature if item.strip()])
    pro_img = urljoin(page_url,tree.xpath('.//div[@class="img swiper-slide text-center"]/img/@src')[0])
    pro_basic = {'产品名称':pro_name,'产品特点':pro_feature,'产品图片':pro_img}
    return pro_basic

# 产品介绍
def parse_intro(pro_name,page_url,tree):
    pro_intro = {}
    if pro_name == 'HANS系列力矩电机':
        text = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]//text()')
        text = ''.join([item.strip() for item in text])
        img1 = urljoin(page_url,tree.xpath('//div[@class="content c1"]/img[1]/@src')[0])
        img2 = urljoin(page_url,tree.xpath('//div[@class="content c1"]/img[2]/@src')[0])
        img3 = urljoin(page_url,tree.xpath('//div[@class="content c1"]/img[3]/@src')[0])
        pro_intro = {'text':text,'img1':img1,'img2':img2,'img3':img3}
    else:
        first_title_tree = tree.xpath('//div[@class="content c1"]/div/span[1]/text()')
        if len(first_title_tree):
            first_title = first_title_tree[0]
            page_text = requests.get(page_url).text
            info = re.findall('<span style="font-size:20px">(.*?)<br />',page_text)
            info = [item.replace('&nbsp;','').replace('<strong>','').replace('</strong>','') for item in info]
            first_title_txt = info[0]
            img_info = re.findall('<img alt="" src="(.*?)" style="height',page_text)
            img_info = [urljoin(page_url,item) for item in img_info]
            img1 = img_info[0]
            img2 = img_info[1]

            second_title = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div/table/tbody/tr/td/div/span/text()')[0]
            second_title_strong = info[1]
            second_title_txt = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div/table/tbody/tr/td/span/text()')[0]
            second_title_txt = ''.join([item.strip() for item in second_title_txt if item.strip()])
            img3 = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div/table/tbody/tr/td/span/img/@src')[0])
            # print(second_title,second_title_strong,second_title_txt)

            third_title = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div/table/tbody/tr/td/div[2]/span/text()')[0]
            tbdata = pd.read_html(page_url,encoding='utf-8')[-2]
            table_dic = parse_table(tbdata=tbdata,kind=2)
            # print(third_title)
            pro_intro = {first_title:first_title_txt,'img1':img1,'img2':img2,
                         second_title:{second_title_strong:second_title_txt},third_title:{'table':table_dic}}

        else:
            text = tree.xpath('//div[@class="content c1"]/text()')[0]
            text = ''.join([item.strip() for item in text if item.strip()])
            img = urljoin(page_url,tree.xpath('//div[@class="content c1"]/img/@src')[0])
            pro_intro = {'text':text,'img':img}
    return pro_intro

# 产品参数
def parse_args(page_url,tree):
    pro_args = {}
    title_tree = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/div[1]//text()')
    if len(title_tree):
        title = title_tree[0].strip()
    else:
        title = tree.xpath('//div[@class="content c2"]/span/text()')[0].strip()
    img_tree = tree.xpath('//div[@class="content c2"]//img[1]/@src')
    if len(img_tree):
        img = urljoin(page_url,img_tree[0])
    else:
        img = ""
    try:
        tbdata = pd.read_html(page_url,encoding='utf-8')[-1]
        table_dic = parse_table(tbdata=tbdata,kind=1)
    except Exception as e:
        table_dic = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/div/img/@src')[0])
    pro_args = {'title':title,'img':img,'table':table_dic}
    return pro_args

# 解析页面
def parse_motor_page(pro_name,page_url,headers):
    pro_dic = {}
    tree = etree.HTML(requests.get(url=page_url,headers=headers).text)
    pro_basic = parse_basic(page_url=page_url,tree=tree)

    pro_intro = parse_intro(pro_name=pro_name,page_url=page_url,tree=tree)
    pro_args = parse_args(page_url=page_url,tree=tree)

    pro_dic = {'基本信息':pro_basic,'产品介绍':pro_intro,'产品参数':pro_args}
    return pro_name,pro_dic

def TorquMotor(headers,filename='torqu_motor.json'):
    final_dic = {}
    torqu_url = 'https://www.hansmotor.com/products/2/c-2/'

    resp = requests.get(url=torqu_url,headers=headers)

    if resp.status_code != 200:
        print(f'状态码{resp.status_code}')
        return None

    tree = etree.HTML(resp.text)
    div_lists = tree.xpath('//div[@class="product-list"]/div/div[@class="box fl text-center relative"]')
    pro_urls,pro_names = [],[]
    
    for div in div_lists:
        pro_url = urljoin(torqu_url,div.xpath('./div[3]//a/@href')[0])
        pro_name = div.xpath('./div[2]/text()')[0]
        pro_names.append(pro_name)
        pro_urls.append(pro_url)
    length = len(pro_urls)

    # 线程池下载 容易403 且函数中xpath解析报错
    # to_do =[]
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     for index in range(length):  # 模拟多个任务
    #         future = executor.submit(parse_motor_page,pro_names[index],pro_urls[index],headers)
    #         to_do.append(future)
    #     for future in concurrent.futures.as_completed(to_do):  # 并发执行
    #         # print(future.result()) # 返回值
    #         pro_name,pro_dic = future.result()
    #         final_dic[pro_name] = pro_dic
            
    for index in range(length):
        print('当前页面是：',pro_urls[index]," 进度: ",index + 1,'/',length)
        pro_name,pro_dic = parse_motor_page(pro_name=pro_name,page_url=pro_urls[index],headers=headers)
        final_dic[pro_names[index]] = pro_dic
        
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")
    return final_dic


if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    TorquMotor(headers=headers,filename='力矩电机.json')