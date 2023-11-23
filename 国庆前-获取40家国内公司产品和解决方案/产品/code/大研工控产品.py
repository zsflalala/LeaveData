import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@class="product_about_r"]/h2/text()')[0].strip()
    pro_img = urljoin(pro_url,tree.xpath('.//div[@class="product_about_l"]/img/@src')[0])
    firstTypeName = tree.xpath('.//div[@class="max_w1280"]/p/a[3]/text()')[0].strip()
    Description,Feature,Parameter = [],[],[]
    desp_text = tree.xpath('.//div[@class="product_about_r"]/p//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    if desp_text != []:
        Description.append({'content':desp_text,'type':'text'})
    
    featrue_text = tree.xpath('.//ul[@class="tab_conbox"]/li[1]//text()')
    featrue_text = ''.join([item.strip() for item in featrue_text]).replace('\xa0','')
    if featrue_text != '':
        Feature.append({'content':featrue_text,'type':'text'})

    img_list = []
    img_tree = tree.xpath('.//ul[@class="tab_conbox"]/li[2]//img')
    for img in img_tree:
        img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
    down_tree = tree.xpath('.//ul[@class="tab_conbox"]/li[3]//a')
    for down in down_tree:
        img_list.append(urljoin(pro_url,down.xpath('./@href')[0]))
    if img_list != []:
        Parameter.append({'content':img_list,'type':'img'})
    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = ''
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def Dayond(headers):
    final_dic = {'pro':[]}
    origion_url = 'http://www.dayond.com/pro.html'
    series_urls = []
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    div_list = tree.xpath('.//div[@class="col-xs-4"]')
    for div in div_list:
        series_urls.append(urljoin(origion_url,div.xpath('./a/@href')[0]))
    for series in series_urls:
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//a[@class="index_product_r_a"]')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for a in a_list:
                pro_url = urljoin(series_urls[0],a.xpath('./@href')[0])
                future = executor.submit(parse_propage,pro_url)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/27条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = Dayond(headers=headers)
    filename=f'大研工控产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    