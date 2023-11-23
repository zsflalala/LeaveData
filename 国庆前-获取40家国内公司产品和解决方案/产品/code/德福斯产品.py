import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    try:
        pro_name = tree.xpath('.//title/text()')[0].strip()
    except IndexError:
        try:
            pro_name = tree.xpath('.//h3/text()')[0].strip()
        except:
            logger.error(f'NameError: {pro_url}')
        return {}
    try:
        firstTypeName = tree.xpath('.//h4/text()')[0].strip()
    except IndexError:
        try:
            firstTypeName = tree.xpath('.//div[@class="posit"]//a')[-1].xpath('./text()')[0].strip()
        except:
            logger.error(f'FirstNameError: {pro_url}')
            return {}
    secondTypeName = ''
    Description,Parameter = [],[]
    des_text = tree.xpath('//*[@id="com_intr"]/div/ul//text()')
    des_text = ''.join([item.strip() for item in des_text])
    para_img = []
    img_tree = tree.xpath('//*[@id="com_intr"]/div/ul//img')
    for img in img_tree:
        para_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    if bool(des_text):
        Description.append({'content':des_text,'type':'text'})
    if bool(para_img):
        Parameter.append({'content':para_img,'type':'img'})

    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = []
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = []
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def Difuss(headers):
    final_dic = {'pro':[]}
    series_urls = [f'http://www.difuss.com/newslist/?id=116&page={i}' for i in range(1,6)]          
    for series in series_urls:
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//table[1]//a')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for a in a_list:
                pro_url = urljoin(series_urls[0],a.xpath('./@href')[0])
                if pro_url.startswith('http://www.difuss.com/'):
                    future = executor.submit(parse_propage,pro_url)
                    to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                if bool(pro_dic):
                    final_dic['pro'].append(pro_dic)
                    logger.info(f'已爬取{len(final_dic["pro"])}/105条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = Difuss(headers=headers)
    filename=f'德福斯产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')