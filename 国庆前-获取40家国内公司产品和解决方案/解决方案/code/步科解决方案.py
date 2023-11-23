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
    solu_text = tree.xpath('.//div[@class="section solution"]//text()')
    desp_text += ''.join([item.strip() for item in solu_text]).replace('\xa0','')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})

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
    urls = [
        'https://www.kinco.cn/articledetail/ydjqrjjfa13.html',
        'https://www.kinco.cn/articledetail/xzjqrwkdjjjfa79.html',
        'https://www.kinco.cn/articledetail/mrihcgzdqjbcydkzxt49.html',
        'https://www.kinco.cn/articledetail/armariummc.html',
        'https://www.kinco.cn/articledetail/armariummc.html',
        'https://www.kinco.cn/articledetail/miotjjfa92.html'
    ]
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
    filename,dic = f'步科解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')