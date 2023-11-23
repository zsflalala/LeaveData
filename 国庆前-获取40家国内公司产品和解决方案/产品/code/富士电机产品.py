import json
import requests
import warnings
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    map_path_box_text = tree.xpath('.//div[@class="map_path_box"]//text()')
    map_path_box_text = ''.join([item.strip() for item in map_path_box_text]).split('>')
    assert len(map_path_box_text) == 5
    firstTypeName = map_path_box_text[2].strip()
    secondTypeName = map_path_box_text[3].strip()
    pro_name = map_path_box_text[-1].strip()
    pro_img = urljoin(pro_url,tree.xpath('.//img[@class="pro_about_img"]/@src')[0])
    Description,Parameter = [],[]
    descri_text = tree.xpath('.//div[@class="ms"]/text()')[0]
    Description.append(descri_text)
    li_list = tree.xpath('.//div[@class="pro_showTxtBox"]/div[@class="hd"]//li')
    div_list = tree.xpath('.//div[@class="pro_showTxtBox"]/div[@class="bd"]/div[@id="pro_nr_box"]')
    assert len(li_list) == len(div_list)
    for i in range(len(li_list)):
        li,div = li_list[i],div_list[i]
        li_text = li.xpath('./text()')[0].strip()
        temp_dic = {li_text:[]}
        img_list = []
        div_text = div.xpath('.//div//text()')
        div_text = ''.join([item.strip() for item in div_text])
        if div_text != '':
            temp_dic[li_text].append({'content':div_text,'type':'text'})
        if div.xpath('.//img') != []:
            for img in div.xpath('.//img'):
                img_list.append(urljoin(pro_url,img.xpath('.//@src')[0]))
            temp_dic[li_text].append({'content':img_list,'type':'img'})
        table_str = []
        if div.xpath('.//table') != []:
            for table in div.xpath('.//table'):
                table_str.append(etree.tostring(table,encoding='utf-8',method='html').decode())
            temp_dic[li_text].append({'content':table_str,'type':'table'})
        Parameter.append(temp_dic)
    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = []
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def FujiElectric(headers):
    final_dic = {'pro':[]}
    series_urls,pro_urls = [],[]
    origion_url = 'https://www.fujielectric.com.cn/product.html'
    resp = requests.get(url=origion_url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="ej_list"]//a')
    for a in a_list:
        series_urls.append(urljoin(origion_url,a.xpath('@href')[0]))
    for series in series_urls:
        resp = requests.get(url=series,headers=headers,verify=False)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="pro_list01"]/li')
        for li in li_list:
            pro_urls.append(urljoin(origion_url,li.xpath('./a[1]/@href')[0]))
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for pro_url in pro_urls:
            future = executor.submit(parse_propage,pro_url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic = future.result()
            final_dic['pro'].append(pro_dic)
            logger.info(f'已爬取{len(final_dic["pro"])}/{len(pro_urls)}条数据')
    return final_dic

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = FujiElectric(headers=headers)
    filename=f'富士电机产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    