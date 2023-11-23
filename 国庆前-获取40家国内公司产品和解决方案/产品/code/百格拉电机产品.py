import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    kind_text = tree.xpath('.//div[@class="ntitle"]//text()')
    kind_text = ''.join([item.strip() for item in kind_text]).split('>')
    assert len(kind_text) == 4
    firstTypeName = kind_text[-2].strip()
    pro_name = kind_text[-1].strip()
    pro_img = urljoin(pro_url,tree.xpath('.//div[@class="cans"]//img/@src')[0])
    Description,Parameter = [],[]
    desp_text = tree.xpath('.//div[@class="cans"]//div[@class="nr"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text]).replace(pro_name,'')
    Description.append(desp_text)
    img_list = tree.xpath('.//div[@class="bd"]//img')
    for img in img_list:
        Parameter.append(urljoin(pro_url,img.xpath('./@src')[0]))
    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = ''
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = []
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def BAIGELA(headers):
    final_dic = {'pro':[]}
    series_urls = [f'http://www.baigela.com/prolist/zh/58/{i}.aspx' for i in range(1,3)] + \
                    [f'http://www.baigela.com/prolist/zh/55/{i}.aspx' for i in range(1,3)] + \
                    ['http://www.baigela.com/prolist/zh/57.aspx','http://www.baigela.com/prolist/zh/56.aspx','http://www.baigela.com/prolist/zh/59.aspx']
    for series in series_urls:
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//div[@class="pdj_list"]//li/a')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for a in a_list:
                pro_url = urljoin(series_urls[0],a.xpath('./@href')[0])
                future = executor.submit(parse_propage,pro_url)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/29条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = BAIGELA(headers=headers)
    filename=f'百格拉电机产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    