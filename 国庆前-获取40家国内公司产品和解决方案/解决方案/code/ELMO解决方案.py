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
    desp_text = ''
    solu_text = tree.xpath('//*[@id="content"]/div/div[1]/div/div/div/div[1]//text()')
    desp_text += ''.join([item.strip() for item in solu_text]).replace('\xa0','')
    solu_text = tree.xpath('//*[@id="content"]/div/div[1]/div/div/div/div[2]//text()')
    desp_text += ''.join([item.strip() for item in solu_text]).replace('\xa0','')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    for producturl in tree.xpath('//*[@id="content"]/div/div[1]/div/div/div/div[3]//a'):
        pro_url = urljoin(solu_url,producturl.xpath('./@href')[0])
        if pro_url not in ProductUrl:
            ProductUrl.append(pro_url)

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
    origion_url = 'https://www.elmomc.com/industries-home/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//*[@id="el-content"]//a')
    for a in a_list:
        url = a.xpath('./@href')[0].strip()
        if url.startswith('http'):
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
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }
    final_dic = get_solution(headers)
    filename,dic = f'ELMO解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')