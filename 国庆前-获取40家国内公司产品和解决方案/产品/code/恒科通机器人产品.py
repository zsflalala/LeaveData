import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url,pro_img,Description):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@class="TuwenBox boxsz fl w100"]/div[1]/text()')[0]
    firstTypeName = tree.xpath('.//div[@class="Currweizhi w100 boxsz mgt30"]/div/a[3]/text()')[0].strip()
    Parameter = []
    img_list = tree.xpath('.//div[@class="tuwenHtml"]//img')
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

def HKTRobot(headers):
    final_dic = {'pro':[]}
    series_urls = []
    origion_url = 'https://www.hkt-robot.com/pages/imglist5.aspx?fid=2&sid=49'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="subnav mgt30 w100 font_poppins"]/div/a')
    for a in a_list:
        series_urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    for series in series_urls:
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        div_list = tree.xpath('.//div[@class="fl boxsz servicesBox"]/div')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for div in div_list:
                pro_url = urljoin(origion_url,div.xpath('./a[1]/@href')[0])
                pro_img = urljoin(origion_url,div.xpath('.//img/@src')[0])
                Description = div.xpath('./a[2]/span[2]/text()')[0]
                logger.info(f'prourl: {pro_url}')
                future = executor.submit(parse_propage,pro_url,pro_img,[Description])
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/15条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = HKTRobot(headers=headers)
    filename=f'恒科通机器人产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    