import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from html import unescape
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def parse_propage(pro_url,firstTypeName='',secondTypeName=''):
    pro_dics = {'pro':[]}
    pro_name,pro_img = '',[]
    Description,Feature,Parameter = [],[],[]
    resp = requests.get(url=pro_url,headers=headers,timeout=(2,10))
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    try:
        pro_name = tree.xpath('.//title/text()')[0].strip()
        img_tree = tree.xpath('.//div[@class="product-detail"]//img')
        for img in img_tree:
            pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
            break
        firstTypeName = tree.xpath('.//li[@class="fnt_24 on"]//text()')[0].strip()
        # Description
        desp_text = tree.xpath('.//div[@class="col-md-6 product-detail-top-l"]//text()')
        desp_text = ''.join([item.strip() for item in desp_text])
        if bool(desp_text):
            Description.append({'content':desp_text,'type':'text'})
        feat_text = tree.xpath('.//div[@class="product-detail-center"]//text()')
        feat_text = ''.join([item.strip() for item in feat_text])
        if bool(feat_text):
            Feature.append({'content':feat_text,'type':'text'})

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
        pro_dics['pro'].append(pro_dic)
    except Exception as e:
        logger.error(f'{e} {pro_url}')
    return pro_dics

def HOLLYSYS(headers):
    final_dic = {'pro':[]}
    urls = []
    series_urls = ['https://www.hollysys.com/cn/product/index_2.html','https://www.hollysys.com/cn/product/index33_3.html','https://www.hollysys.com/cn/product/index33_2.html','https://www.hollysys.com/cn/product/index81.html','https://www.hollysys.com/cn/product/index69.html','https://www.hollysys.com/cn/product/index34.html','https://www.hollysys.com/cn/product/index33.html','https://www.hollysys.com/cn/product/index.html']
    for series_url in series_urls:
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('//*[@class="product-main"]//a')
        for a in a_list:
            url = urljoin(series_url,a.xpath('./@href')[0])
            if url.startswith('https://www.hollysys.com/'):
                urls.append(url)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            future = executor.submit(parse_propage,url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dics = future.result()
            final_dic['pro'] += pro_dics['pro']
            logger.success(f'已爬取{len(final_dic["pro"])}/{len(urls)}条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'acw_tc=2760778216994333499288924eaa51d8c1a5d5913c058897233ee2657d2d95; user_sid=e556c9bc3f; ASP.NET_SessionId=uesjszkygqeeyy5wh15tfvbf; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C5625DFD1C979837BFF04=1AjpfUmRQ4WQv/rF7PQ0Q6SIyKip986cj29q2AVn5sr4s83coNmYyUCqSVgxrvkb; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C562590675F0802DD8505D0E19FED84200C90BE3AF119DE6F4B6853122BC44220B57FD4B51CD15FD8CACC=A16tsG/ZlRYwt75S4oDoIxSS3Rt2/BB37nEdW9/GuyPpv+DjYXhNyZ6+Q+S8K32L; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C562590675F0802DD8505D0E19FED84200C907739DBFF7F1AC61695B51426082C7281CFCBC92943ADF02F=eVCJ86M12AoFoNQ8FkBISWmZdJFOvtP2b8st5QhY3l0vaONl9QSYwaYppvn0xnQg',
        'Referer':'https://www.hollysys.com/cn/product/trade.html',
    }
    final_dic = HOLLYSYS(headers=headers)
    filename=f'和利时产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    