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
    tags = []
    a_list = tree.xpath('//*[@id="block-koll-forest-breadcrumbs"]/nav/ol//a')
    for a in a_list:
        tags.append(a.xpath('./text()')[0].strip())
    pro_name = tags[-1]
    try:
        firstTypeName,secondTypeName = tags[2],tags[3]
    except:
        logger.warning(f'NameError : {tags}')
        firstTypeName = ''
        secondTypeName = ''
    pro_img = []
    img_tree = tree.xpath('//div[@class="card carousel-item active"]//img')
    for img in img_tree:
        pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))

    Description,Feature = [],[]
    desp_text = tree.xpath('//*[@id="block-koll-forest-content"]/div/div[1]/div/div/div[2]/div[1]//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    Description.append({'content':desp_text,'type':'text'})
    fea_text = tree.xpath('//*[@id="block-koll-forest-content"]/div/div[2]/div[2]/div[1]/div/div/div/div/div[2]//text()')
    fea_text = ''.join([item.strip() for item in fea_text])
    Feature.append({'content':fea_text,'type':'text'})
    
    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = []
    return pro_dic

def KOLLMORGEN(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.kollmorgen.cn/zh-cn/products/linear-positioners/rodless-positioners/%E6%97%A0%E6%9D%86%E5%AE%9A%E4%BD%8D%E5%99%A8'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    urls,pro_urls = [],[]
    a_list = tree.xpath('//*[@id="block-mainnavigation"]/ul//a')
    for a in a_list:
        urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    for url in urls:
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        grid_tree = tree.xpath('.//div[@class="grid size3"]//a')
        if bool(grid_tree):
            for grid in grid_tree:
                new_url = urljoin(origion_url,grid.xpath('./@href')[0])
                if new_url not in urls:
                    urls.append(new_url)
                    logger.info(f'one url in! => {len(urls)}')
        else:
            pro_urls.append(url)
            logger.info(f'ProUrl in! => {len(pro_urls)}')
    pro_urls = list(set(pro_urls))
    logger.info(f'ProUrlLength {len(pro_urls)}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for pro_url in pro_urls:
            future = executor.submit(parse_propage,pro_url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic = future.result()
            final_dic['pro'].append(pro_dic)
            logger.info(f'已爬取{len(final_dic["pro"])}/{len(pro_urls)}条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = KOLLMORGEN(headers=headers)
    filename=f'科尔摩根产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    