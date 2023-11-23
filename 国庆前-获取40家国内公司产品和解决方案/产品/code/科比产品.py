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

    pro_name = tree.xpath('.//div[@class="maintitle biggestfz container-width"]/text()')[0].strip()
    img_tree = tree.xpath('.//div[@class="swiper-container banner-container"]//img')
    for img in img_tree:
        pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    tag_list = tree.xpath('.//div[@class="breadcrumbs cp2 container-width flex-left"]//a/text()')
    if len(tag_list) > 3:
        for name in tag_list:
            if name != '首页' and name != '应用' and name != '产品':
                firstTypeName = name
                break
    if len(tag_list) > 5:
        secondTypeName = tree.xpath('.//div[@class="breadcrumbs cp2 container-width flex-left"]/a[5]/text()')[0].strip()
    # Description
    desp_text = tree.xpath('.//div[@class="textpart1 fl"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    feat_text = tree.xpath('.//div[@class="other"]//text()')
    feat_text = ''.join([item.strip() for item in feat_text])
    if bool(feat_text):
        Feature.append({'content':feat_text,'type':'text'})
    feat_img = []
    for img in tree.xpath('.//div[@class="flex-sb fullwidth mt4"]//img'):
        feat_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    if bool(feat_img):
        Feature.append({'content':feat_img,'type':'img'})

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
    if not bool(Description) and not bool(Feature):
        isError = 1
    return pro_dic,isError

def HOLLYSYS(headers):
    final_dic = {'pro':[]}
    origion_url = 'http://www.keb.cn/site/deviceDetail/2'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    urls = []
    a_list = tree.xpath('.//div[@class="item transition6 fl"]')[0].xpath('//li[@class="fourthTitle halfwidth" or @class="fourthTitle"]//a')
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
            logger.success(f'已爬取{len(final_dic["pro"])}/82条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'acw_tc=2760778216994333499288924eaa51d8c1a5d5913c058897233ee2657d2d95; user_sid=e556c9bc3f; ASP.NET_SessionId=uesjszkygqeeyy5wh15tfvbf; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C5625DFD1C979837BFF04=1AjpfUmRQ4WQv/rF7PQ0Q6SIyKip986cj29q2AVn5sr4s83coNmYyUCqSVgxrvkb; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C562590675F0802DD8505D0E19FED84200C90BE3AF119DE6F4B6853122BC44220B57FD4B51CD15FD8CACC=A16tsG/ZlRYwt75S4oDoIxSS3Rt2/BB37nEdW9/GuyPpv+DjYXhNyZ6+Q+S8K32L; FE9DB11CC9D6C9EB9E11C06513914C5F2CB155127E47DC8BF00918BAAF6E7FEE5CE2B6CDFF7595289A5C6CA206833C457FB287871A4C562590675F0802DD8505D0E19FED84200C907739DBFF7F1AC61695B51426082C7281CFCBC92943ADF02F=eVCJ86M12AoFoNQ8FkBISWmZdJFOvtP2b8st5QhY3l0vaONl9QSYwaYppvn0xnQg',
        'Referer':'https://www.hollysys.com/cn/product/trade.html',
    }
    final_dic = HOLLYSYS(headers=headers)
    filename=f'科比产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    