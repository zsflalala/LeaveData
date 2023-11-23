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
    tree = etree.HTML(resp.text)

    title = tree.xpath('.//title/text()')[0].strip()
    solu_tree = tree.xpath('.//div[@class="section group featurePlain" or @class="para-bgimg-1" or @class="section group leadStory"]')
    if bool(solu_tree):
        desp_text,desp_img = '',[]
        for solu in solu_tree:
            solu_text = solu.xpath('.//text()')
            desp_text += ''.join([item.strip() for item in solu_text]).replace('\xa0','')
            for img in solu.xpath('.//img'):
                desp_img.append(urljoin(solu_url,img.xpath('./@src')[0]))
        if bool(desp_text):
            Description.append({'content':desp_text,'type':'text'})
        if bool(desp_img):
            Description.append({'content':desp_img,'type':'img'})
    else:
        solu_tree = tree.xpath('.//div[@class="tabView"]//table')
        for table in solu_tree:
            table_str = etree.tostring(table,encoding='utf-8').decode()
            Description.append({'content':table_str,'type':'table'})

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
    origion_url = 'http://www.triomotion.cn/?list_91/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    urls = []
    div_list = tree.xpath('.//div[@class="tabs"]//div')
    for div in div_list:
        urls.append(urljoin(origion_url,div.xpath('./@onclick')[0].replace('location.href=\'','').replace('\'','')))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(parse_solu,url))
        for future in concurrent.futures.as_completed(to_do):
            solu_dic = future.result()
            final_dic['pro'].append(solu_dic)
            logger.success(f'爬取方案{len(final_dic["pro"])}/12条数据')
    return final_dic

if __name__ == "__main__":
    logger.add('runtime.log',retention='1 day')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'翠欧运动解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')