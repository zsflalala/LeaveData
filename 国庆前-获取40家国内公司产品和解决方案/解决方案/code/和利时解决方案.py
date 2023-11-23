import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


@logger.catch
def parse_solu(solu_url):
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    firstTypeName = tree.xpath('.//li[@class="fnt_24 on"]/a/text()')[0].strip()
    try:
        title = tree.xpath('.//title/text()')[0].strip()
    except:
        title = tree.xpath('.//h4[1]/text()')[0].strip()
    Description,ProductUrl = [],[]
    desp_text = tree.xpath('.//div[@class="product-detail-top"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    desp_text2 = tree.xpath('.//div[@class="product-detail-center"]//text()')
    desp_text2 = ''.join([item.strip() for item in desp_text2])
    text = desp_text + desp_text2
    Description.append({'content':text,'type':'text'})
    images = []
    img_tree = tree.xpath('//div[@class="product-detail-top"]//img')
    for img in img_tree:
        images.append(urljoin(solu_url,img.xpath('./@src')[0]))
    Description.append({'content':images,'type':'image'})
    product_tree = tree.xpath('.//div[@class="product-main"]//a')
    for product in product_tree:
        ProductUrl.append(product.xpath('./@href')[0])
    
    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    return solu_dic

def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.hollysys.com/cn/product/solution.html'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//div[@class="product-tab fixed row"]//a')
    series_urls,solu_urls = [],[]
    for a in a_list:
        series_urls.append(a.xpath('./@href')[0])
    for series_url in series_urls:
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//div[@class="product-main product-solution"]//a')
        for a in a_list:
            solu_url = a.xpath('./@href')[0]
            if solu_url.startswith('https://www.hollysys.com/cn'):
                solu_urls.append(solu_url)
    solu_urls += ['https://www.hollysys.com/cn/content/details36_2294.html','https://www.hollysys.com/cn/content/details82_1861.html']
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for solu_url in solu_urls:
            to_do.append(executor.submit(parse_solu,solu_url))
        for future in concurrent.futures.as_completed(to_do):
            solu_dic = future.result()
            final_dic['pro'].append(solu_dic)
            logger.info(f'爬取方案{len(final_dic["pro"])}/32条数据')
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