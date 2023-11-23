import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from html import unescape
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def parse_propage(pro_url,id,firstTypeName='',secondTypeName=''):
    pro_name,pro_img = '',[]
    Description,Feature,Parameter = [],[],[]
    page_url = f'https://www.hiconics.com/cn/product/product-detail/prod-detail?productId={id}'
    page_resp = requests.get(url=page_url,headers=headers)
    resp = requests.get(url=pro_url,headers=headers,timeout=(2,10))
    data = resp.json()['data']

    pro_name = data['name']
    pro_img.append(data['mainPic'])
    # Description
    desp_text = data['description']
    Description.append({'content':desp_text,'type':'text'})
    desp_img = []
    if bool(data['productDetail']):
        tree = etree.HTML(data['productDetail'])
        for img in tree.xpath('.//img'):
            desp_img.append(img.xpath('./@src')[0])
        Description.append({'content':desp_img,'type':'img'})
    else:
        logger.warning(f'DetailWarning : {pro_url}')
    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = page_url
    pro_dic['ProductHTML'] = unescape(page_resp.text.strip())
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def HOLLYSYS(headers):
    final_dic = {'pro':[]}
    Ids = []
    post_data = {"page":2,"pageSize":9,"dataCode":"HICONICS","dataLanguage":"zh","categoryId":"100256","categoryLevel":2,"labelIds":[]}
    post_url = 'https://ibs-hk.midea.com/api/product-mgmt/techAemProductApi/getAemProductList'
    categoryIds = ['100256','100255','100271','100273','100270','100258']
    resp = requests.post(url=post_url,json=post_data,headers=headers)
    list = resp.json()['data']['list']
    for item in list:
        Ids.append(item['id'])
    post_data['page'] = 1
    for categoryId in categoryIds:
        post_data['categoryId'] = categoryId
        resp = requests.post(url=post_url,json=post_data,headers=headers)
        list = resp.json()['data']['list']
        for item in list:
            Ids.append(item['id'])
    logger.info(f'{Ids}')

    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for id in Ids:
            url = f'https://ibs-hk.midea.com/api/product-mgmt/techAemProductApi/getAemProductDetail?dataCode=HICONICS&productId={id}&dataLanguage=zh&_=1699492430793'
            future = executor.submit(parse_propage,url,id)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic = future.result()
            final_dic['pro'].append(pro_dic)
            logger.success(f'已爬取{len(final_dic["pro"])}/{len(Ids)}条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'acw_tc=2760778216994333499288924eaa51d8c1a5d5913c058897233ee2657d2d95; user_sid=e556c9bc3f; ASP.NET_SessionId=uesjszkygqeeyy5wh15tfvbf; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C5625DFD1C979837BFF04=1AjpfUmRQ4WQv/rF7PQ0Q6SIyKip986cj29q2AVn5sr4s83coNmYyUCqSVgxrvkb; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C562590675F0802DD8505D0E19FED84200C90BE3AF119DE6F4B6853122BC44220B57FD4B51CD15FD8CACC=A16tsG/ZlRYwt75S4oDoIxSS3Rt2/BB37nEdW9/GuyPpv+DjYXhNyZ6+Q+S8K32L; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C562590675F0802DD8505D0E19FED84200C907739DBFF7F1AC61695B51426082C7281CFCBC92943ADF02F=eVCJ86M12AoFoNQ8FkBISWmZdJFOvtP2b8st5QhY3l0vaONl9QSYwaYppvn0xnQg',
        'Referer':'https://www.hollysys.com/cn/product/trade.html',
    }
    final_dic = HOLLYSYS(headers=headers)
    filename=f'合康新能产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    