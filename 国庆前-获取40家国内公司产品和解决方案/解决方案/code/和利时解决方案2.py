import json
import requests
from lxml import etree
from loguru import logger
from html import unescape
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


@logger.catch
def parse_solu(solu_url,firstTypeName='',secondTypeName=''):
    title = ''
    ProductUrl,Description = [],[]
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    title = tree.xpath('.//title/text()')[0].strip()
    firstTypeName = tree.xpath('.//li[@class="fnt_24 on"]//text()')[0].strip()
    desp_text = ''
    solu_text = tree.xpath('.//div[@class="product-detail-top" or @class="product-detail-center product-detail-center-solution"]//text()')
    desp_text += ''.join([item.strip() for item in solu_text]).replace('\xa0','')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    for producturl in tree.xpath('.//div[@class="product-detail-bottom"]//a'):
        ProductUrl.append(urljoin(solu_url,producturl.xpath('./@href')[0]))

    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = secondTypeName
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = unescape(resp.text.strip())
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    return solu_dic

def get_solution(headers):
    final_dic = {'pro':[]}
    urls = []
    series_urls = [
        'https://www.hollysys.com/cn/product/solution.html',
        'https://www.hollysys.com/cn/product/solution36.html',
        'https://www.hollysys.com/cn/product/solution37.html',
        'https://www.hollysys.com/cn/product/solution72.html',
        'https://www.hollysys.com/cn/product/solution82.html',
        'https://www.hollysys.com/cn/product/solution82_2.html',
        'https://www.hollysys.com/cn/product/solution36_2.html'
    ]
    for series_url in series_urls:
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('//*[@class="product-main product-solution"]//a')
        for a in a_list:
            url = urljoin(series_url,a.xpath('./@href')[0])
            if url.startswith('https://www.hollysys.com/') and url not in series_urls:
                urls.append(url)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(parse_solu,url))
        for future in concurrent.futures.as_completed(to_do):
            solu_dic = future.result()
            final_dic['pro'].append(solu_dic)
            logger.success(f'爬取方案{len(final_dic["pro"])}/{len(urls)}条数据')
    return final_dic

if __name__ == "__main__":
    logger.add('runtime.log',retention='1 day')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'和利时解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')