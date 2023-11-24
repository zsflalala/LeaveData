import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin

def parse_serise(series,pro_urls,headers):
    pro_dic = {}
    for url in pro_urls:
        temp_dic = {}
        resp = requests.get(url=url,headers=headers)
        tree = etree.HTML(resp.text)
        if series == '新能源汽车电驱系列':
            pro_name = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/div/div/text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            if pro_name == '':
                pro_name = tree.xpath('.//div[@class="ytable-cell left"]/div[@class="tit"]/span/text()')[0]
            pro_desc = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/dd//text()')
            if pro_desc == []:
                pro_desc = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/p//text()')
            pro_desc = ''.join([item.strip() for item in pro_desc])
        else:
            pro_name = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/div//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_desc = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/p//text()')
            pro_desc = ''.join([item.strip() for item in pro_desc])

        pro_img = urljoin(url,tree.xpath('.//div[@class="pic"]/img/@src')[0]) 
        
        pro_feature = []
        dl_list = tree.xpath('.//div[@class="box_item box2"]/div/dl')
        if pro_feature == [] and pro_name == '主驱电机控制器':
            dl_list = tree.xpath('/html/body/div[2]/div[2]/div[2]/dl/dd')
        for dd in dl_list:
            feature = dd.xpath('.//text()')
            feature = ''.join([item.strip() for item in feature])
            pro_feature.append(feature)
        

        application = []
        li_list = tree.xpath('/html/body/div[2]/div[3]/div/ul/div/div/li')
        for li in li_list:
            application.append(li.xpath('//text()')[0])
            
        args = []
        li_list = tree.xpath('.//div[@class="box_item box4"]//li')
        for li in li_list:
            args.append(urljoin(url,li.xpath('.//div[@class="pic"]/img/@src')[0]))
        
        download = {}
        boxitem_box5 = tree.xpath('.//div[@class="box_item box5"]')
        if boxitem_box5 != []:
            ul_list = boxitem_box5[0].xpath('./div/ul')
            for ul in ul_list:
                data_name = ul.xpath('./@data-name')[0]
                download[data_name] = []
                li_list = ul.xpath('./li')
                for li in li_list:
                    download[data_name].append(urljoin(url,li.xpath('./a/@href')[0]))
        temp_dic = {'产品名称':pro_name,'产品介绍':pro_desc,'产品图片':pro_img,'产品特点':pro_feature,
                    '产品参数':args,'资料下载':download}
        pro_dic[pro_name] = temp_dic
    return pro_dic

def HYSIS(headers,filename='hysis.json'):
    final_dic = {}
    url = 'http://www.physis.com.cn/ProductCenter3992/index.aspx?lcid=31'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    div_list = tree.xpath('.//div[@class="product_ls"]/div')
    for div in div_list:
        series = div.xpath('./div/div/span/text()')[0]
        pro_urls = []
        li_list = div.xpath('.//li')
        for li in li_list:
            pro_urls.append(urljoin(url,li.xpath('./a/@href')[0]))
        if series == 'OSAI控制系统':
            continue
        pro_dic = parse_serise(series,pro_urls,headers)
        final_dic[series] = pro_dic
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取完成，存储在{filename}中.')

if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    HYSIS(headers=headers,filename='菲仕.json')