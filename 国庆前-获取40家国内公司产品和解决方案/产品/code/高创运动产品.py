import re
import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url,firstTypeName,secondTypeName):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@class="proDet-show-title mt10 fs48 fmB color pb20 por"]/text()')[0].strip()
    pro_img = []
    img_list = tree.xpath('.//div[@class="swiper-container swiper-no-swiping"]//img')
    for img in img_list:
        pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))

    Description,Feature,Parameter = [],[],[]
    descpt_text = tree.xpath('.//div[@class="proDet-show-text fs18 lh36 c5 fmL mt30"]//text()')
    descpt_text = ''.join([item.strip() for item in descpt_text if item.strip()])
    if descpt_text != '':
        Description.append({'content':descpt_text,'type':'text'})

    feature_text = tree.xpath('.//div[@class="proDetTx-text center fs18 lh30 c4 mt20"]/text()')
    Feature = [item.strip() for item in feature_text if item.strip()]

    para_movie = []
    movie_tree = tree.xpath('.//div[@class="proDet-show-btn flex mt50"]/a[2]')
    for movie in movie_tree:
        para_movie.append(urljoin(pro_url,movie.xpath('./@videosrc')[0]))
    para_img = []
    down_tree = tree.xpath('.//div[@class="downTable-group mt30"]//a')
    for a in down_tree:
        link = a.xpath('./@href')[0]
        if link:
            para_img.append(urljoin(pro_url,link))
    if para_movie != []:
        Parameter.append({'content':para_img,'type':'movie'})
    if para_img != []:
        Parameter.append({'content':para_img,'type':'download'})

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
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def POWERLAND(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.servotronix.cn/ydkzq'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('/html/body/div[2]/div[2]/div/div[1]/a')              
    for a in a_list:
        firstTypeName = a.xpath('./text()')[0].strip()
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        pro_list = tree.xpath('.//div[@class="proList mt10 flex"]/a')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for product in pro_list:
                pro_url = urljoin(origion_url,product.xpath('./@href')[0])
                future = executor.submit(parse_propage,pro_url,firstTypeName,'')
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/22条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = POWERLAND(headers=headers)
    filename=f'高创运动产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    