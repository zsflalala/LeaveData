import re
import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def parse_propage(origion_url,div,resp,firstTypeName,secondTypeName):
    title = div.xpath('.//div[@class="team-text pera-content text-center headline"]/p[1]/text()')[0]
    pro_img = urljoin(origion_url,div.xpath('.//img/@src')[0])
    onclick = div.xpath('./@onclick')[0]
    pro_url = urljoin(origion_url, re.findall("'(.*?)'",onclick)[0])
    resp = requests.get(url=pro_url,headers=headers)
    tree = etree.HTML(resp.text)
    overview,parameter,download = [],[],[]
    overview_img_tree = tree.xpath('.//div[@class="contents clearfix"]/div[1]//img')
    for img in overview_img_tree:
        overview.append(urljoin(origion_url,img.xpath('./@src')[0]))
    parameter_img_tree = tree.xpath('.//div[@class="contents clearfix"]/div[2]//img')
    for img in parameter_img_tree:
        parameter.append(urljoin(origion_url,img.xpath('./@src')[0]))
    download_tree = tree.xpath('.//*[@id="eltron-team"]/div/div[2]/div/div[2]/div[3]//a')
    for a in download_tree:
        download.append(urljoin(origion_url,a.xpath('./@href')[0]))
    # logger.info(f'title: {title}')
    # logger.info(f'overview: {overview}')
    # logger.info(f'parameter: {parameter}')
    # logger.info(f'download: {download}')
    pro_dic = {}
    pro_dic['ProductName'] = title
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = {'产品概览':overview,'资料下载':download}
    pro_dic['ProductDetail']['Feature'] = []
    pro_dic['ProductDetail']['Parameter'] = parameter
    return pro_dic

def ESTUN(headers):
    final_dic = {'pro':[]}
    series_urls = []
    origion_url = 'http://www.estun.com/?list_1/'
    resp = requests.Session().get(url=origion_url,headers=headers,verify=False)
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//dl[@class="nr_dl type_dl"]')[0].xpath('.//a')
    del a_list[-1],a_list[-1]
    pro_series_urls = [f'http://www.estun.com/?list_{i}/' for i in [16,17,18,9,134]]
    for a in a_list:
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        if series_url not in pro_series_urls:
            series_urls.append(series_url)
    for url in series_urls:
        resp = requests.Session().get(url=url,headers=headers,verify=False)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        firstTypeName = tree.xpath('//*[@id="breadcrumb"]/div[2]/div/h2/text()')[0].strip()
        a_list = tree.xpath('.//div[@class="col-lg-3 col-md-6"]/a')
        for a in a_list:
            secondTypeName = a.xpath('.//h3/text()')[0]
            kind_url = urljoin(origion_url,a.xpath('./@href')[0])
            resp = requests.get(url=kind_url,headers=headers)
            tree = etree.HTML(resp.text)
            div_list = tree.xpath('.//div[@class="col-lg-3 col-md-6"]')
            for div in div_list:
                pro_dic = parse_propage(origion_url,div,resp,firstTypeName,secondTypeName)
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/138条数据')
    for url in pro_series_urls:
        resp = requests.Session().get(url=url,headers=headers,verify=False)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        firstTypeName = tree.xpath('//*[@id="breadcrumb"]/div[2]/div/h2/text()')[0].strip()
        div_list = tree.xpath('.//div[@class="col-lg-3 col-md-6"]')
        for div in div_list:
            pro_dic = parse_propage(origion_url,div,resp,firstTypeName,'')
            final_dic['pro'].append(pro_dic)
            logger.info(f'已爬取{len(final_dic["pro"])}/138条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = ESTUN(headers=headers)
    filename=f'埃斯顿产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    