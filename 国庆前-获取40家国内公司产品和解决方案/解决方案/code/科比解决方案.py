import json
import requests
from lxml import etree
from loguru import logger
from html import unescape
from urllib.parse import urljoin
from w3lib.html import remove_comments
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


@logger.catch
def parse_solu(solu_url,firstTypeName='',secondTypeName=''):
    title = ''
    ProductUrl,Description = [],[]
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(remove_comments(resp.text))
    title = tree.xpath('.//div[@class="maintitle biggestfz container-width"]/text()')[0].strip()
    tag_list = tree.xpath('.//div[@class="breadcrumbs cp2 container-width flex-left"]/a/text()')
    for name in tag_list:
        if name != '首页' and name != '应用' and name != '产品':
            firstTypeName = name

    desp_text = tree.xpath('.//div[@class="left fl"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text]).replace('\xa0','')
    no_tag_list = ['//script','//style','//noscript','//iframe','//svg','//button']
    for no_tag in no_tag_list:
        no_tag_tree = tree.xpath('.//div[@class="left fl"]'+no_tag)
        for tag in no_tag_tree:
            tag_text = tag.xpath('.//text()')
            tag_text = ''.join([item.strip() for item in tag_text])
            desp_text = desp_text.replace(tag_text,'')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    for producturl in tree.xpath('.//div[@class="rightMenu"]/div[1]//div[@class="fourth"]//a'):
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
    origion_url = 'http://www.keb.cn/site/plasticMachinery'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//div[@class="item transition6 fl"]')[1].xpath('.//div[@class="smtit fl"]/div//a')
    for a in a_list:
        urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
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
    filename,dic = f'科比解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')