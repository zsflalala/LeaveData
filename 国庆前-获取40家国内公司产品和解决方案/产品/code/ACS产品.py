import re
import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url,firstTypeName):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//h1/text()')[0].strip()
    pro_img = []
    img_tree = tree.xpath('.//div[@class="gallery__slider"]/div[2]//a')
    for img in img_tree:
        pro_img.append(urljoin(pro_url,img.xpath('./@href')[0]))
    Description,Feature,Parameter = [],[],[]
    descpt_text = tree.xpath('.//div[@data-tab-content="description"]/div/div[1]//text()')
    descpt_text = ''.join([item.strip() for item in descpt_text])
    Description.append({'content':descpt_text,'type':'text'})
    li_list = tree.xpath('.//li[@class="list__entry  "]')
    try:
        for li in li_list:
            featrue_text = li.xpath('.//text()')
            featrue_text = ''.join([item.strip() for item in featrue_text if item.strip()])
            Feature.append(featrue_text)
    except:
        logger.error(f'FeatrueError: {pro_url}')
    table_tree = tree.xpath('.//div[@data-tab-content="specification"]//table')
    for table in table_tree:
        table_str = etree.tostring(table,encoding='utf-8').decode()
        Parameter.append({'content':table_str,'type':'table'})
    para_text = tree.xpath('.//div[@data-tab-content="specification"]//div[@class="nota product_styles"]//text()')
    para_text = ''.join([item.strip() for item in para_text if item.strip()])
    if bool(para_text):
        Parameter.append({'content':para_text,'type':'text'})
    a_list = tree.xpath('.//div[@data-tab-content="downloads"]//div[@class="product_downloads"]//a')
    for a in a_list:
        link = a.xpath('./@href')
        if bool(link):
            Parameter.append({'content':urljoin(pro_url,link[0]),'type':'download'})

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

def POWERLAND(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.pi-china.cn/zh_cn/products/productfinder'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//*[@id="ce35700"]/div[5]/div/div/div/a')              
    for a in a_list:
        firstTypeName = a.xpath('./h3/text()')[0].strip()
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        div_list = tree.xpath('.//div[@class="col-xs-12 col-sm-6 col-md-3"]')
        span_tree = tree.xpath('.//span[@class="data-articleloader-pageurl"]')
        for span in span_tree:
            more_url = urljoin(origion_url,span.xpath('./@data-articleloader-pageurl')[0])
            resp = requests.get(url=more_url,headers=headers)
            resp.encoding = 'utf-8'
            tree = etree.HTML(resp.text)
            div_list += tree.xpath('.//div[@class="col-xs-12 col-sm-6 col-md-3"]')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for div in div_list:
                pro_url = urljoin(origion_url,div.xpath('.//a/@href')[0])
                future = executor.submit(parse_propage,pro_url,firstTypeName)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/299条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'BAIDUID_BFESS=78CEDFE318F24BC4128A939872361B17:FG=1; ab_jid=a3456b38b8f3bd4c38ef1f1fc7609a0b4d86; ab_jid_BFESS=a3456b38b8f3bd4c38ef1f1fc7609a0b4d86; ab_bid=3939e17ab42567a143e60bd959945decd98f; ab_sr=1.0.1_NjFiYzc1MGUyMzg5MTRlY2UwZTQ5YTMzYjhlZDhlZmRjNTdhMzA4OTI2ZjkxYjc0ODBiNDc1NTIzNDJkMWRiYWVkZTU3ZWFjOTZiMzAzNjg4YzI1NmM5ZDdjNzMwMmJmNDIxN2M3OGM4MGRmNTk5OTc0ZTgwNGFhZGUxOTBjNjgzNzM0M2FmNDgxN2FlNWJjZjczZWU3MGVjNGU1YjA3NQ==',
        'Referer':'https://www.pi-china.cn/zh_cn/products/productfinder?tx_avphysikinstrumente_productfinder%5Bcontroller%5D=ProductFinder&tx_avphysikinstrumente_productfinder%5BparentCategory%5D=41&cHash=d0c83b439905697a7226d0024cfa07c6',
    }
    final_dic = POWERLAND(headers=headers)
    filename=f'ACS产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    