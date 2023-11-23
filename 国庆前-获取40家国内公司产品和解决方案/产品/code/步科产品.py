import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from html import unescape
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

@logger.catch
def parse_propage(pro_url,firstTypeName='',secondTypeName=''):
    isError = 0
    pro_name,pro_img = '',[]
    Description,Feature,Parameter = [],[],[]
    resp = requests.get(url=pro_url,headers=headers,timeout=(2,10))
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    try:
        pro_name = tree.xpath('.//div[@class="pror-tit"]/text()')[0].strip()
    except:
        logger.error(f'NameError : {pro_url}')
    img_tree = tree.xpath('.//ul[@id="itemsUl"]//img')
    for img in img_tree:
        pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    tag_list = tree.xpath('.//div[@class="crumb"]//a/text()')
    if len(tag_list) >= 3:
        for name in tag_list:
            if name != '首页' and name != '应用' and name != '产品':
                firstTypeName = name
                break
    # Description
    desp_text = tree.xpath('.//div[@class="pror-dec"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    
    para_text = tree.xpath('.//div[@class="proi-mid"]//text()')
    para_text = ''.join([item.strip() for item in para_text])
    if bool(para_text):
        Parameter.append({'content':para_text,'type':'text'})
    pdf_list = []
    pdf_tree = tree.xpath('.//div[@class="proi-bot"]//a')
    for pdf in pdf_tree:
        pdf_url = pdf.xpath('./@href')[0]
        if pdf_url.endswith('.pdf'):
            pdf_list.append(pdf_url)
    if bool(pdf_list):
        Parameter.append({'content':pdf_list,'type':'pdf'})

    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = unescape(resp.text.strip())
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    if not bool(Description) and not bool(Feature) and not bool(pro_name):
        isError = 1
    return pro_dic,isError

def Kinco(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.kinco.cn/product/hmi.html'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    urls,series_urls = [],[]
    a_list = tree.xpath('/html/body/div[1]/div/ul/li[2]//dd//a')
    for a in a_list:
        series_urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    series_urls = list(set(series_urls))
    logger.info(f'SeriesUrlLength {len(series_urls)}')
    for series_url in series_urls:
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//div[@class="h900"]//a')
        for a in a_list:
            urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            future = executor.submit(parse_propage,url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic,isError = future.result()
            if not isError:
               final_dic['pro'].append(pro_dic)
            logger.success(f'已爬取{len(final_dic["pro"])}/{len(urls)}条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = Kinco(headers=headers)
    filename=f'步科产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    