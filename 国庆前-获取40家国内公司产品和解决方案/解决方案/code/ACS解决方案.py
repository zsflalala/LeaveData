import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


@logger.catch
def parse_solu(solu_url,firstTypeName):
    resp = requests.get(url=solu_url,headers=headers)
    tree = etree.HTML(resp.text)
    try:
        title = tree.xpath('.//div[@class="ce-textimage"]/header/h1/text()')[0].strip()
    except:
        title = tree.xpath('.//h1[@class="header header-position-center "]/text()')[0].strip()
    Description = []
    desp_text = tree.xpath('.//div[@class="ce-textimage"]')[0].xpath('./div//text()')
    desp_text = ''.join([item.strip() for item in desp_text]).replace('\xa0','')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    div_list = tree.xpath('.//div[@class="three-column-grid row"]/div')
    for div in div_list:
        desp_text2 = div.xpath('.//text()')
        desp_text2 = ''.join([item.strip() for item in desp_text2 if item.strip()])
        if bool(desp_text2):
            Description.append({'content':desp_text2,'type':'text'})
    movie_tree = tree.xpath('.//video')
    for movie in movie_tree:
        movie_url = urljoin(solu_url,movie.xpath('./@src')[0])
        Description.append({'content':movie_url,'type':'movie'})
    img_list = []
    img_tree = tree.xpath('.//div[@class="ce-outer"]//img')
    if bool(img_tree):
        img_list.append(urljoin(solu_url,img_tree[0].xpath('./@src')[0]))
        Description.append({'content':img_list,'type':'img'})
    Feature = []
    div_list = tree.xpath('.//div[@class="col-sm-12 col-xs-12 highlights_inner"]')
    for div in div_list:
        feature_text = div.xpath('.//text()')
        feature_text = ''.join([item.strip() for item in feature_text if item.strip()])
        Feature.append(feature_text)
    Download = []
    a_list = tree.xpath('.//a')
    for a in a_list:
        url_tree = a.xpath('./@href')
        if bool(url_tree) and url_tree[0].endswith('.pdf'):
            Download.append(urljoin(solu_url,url_tree[0]))
    ProductUrl = []
    try:
        a_list = tree.xpath('.//div[@class="ce-menu ce-menu-pagegrid "]//a')
        for a in a_list:
            ProductUrl.append(urljoin(solu_url,a.xpath('./@href')[0]))
    except:
        a_list = tree.xpath('.//div[@class="swiper-container swiper-container-overflow swiper-container-initialized swiper-container-horizontal swiper-container-pointer-events"]//a')
        for a in a_list:
            ProductUrl.append(urljoin(solu_url,a.xpath('./@href')[0]))
    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = {'方案介绍':Description,'方案特点':Feature,'下载链接':Download}
    solu_dic['ProductUrl'] = ProductUrl
    return solu_dic

def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.pi-china.cn/zh_cn/knowledge-center/product-and-system-demonstrators'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    div_list = tree.xpath('//*[@id="page_main"]/div')
    del div_list[0]
    for div in div_list:
        firstTypeName = div.xpath('./h3//text()')
        firstTypeName = ''.join([item.strip() for item in firstTypeName])
        a_list = div.xpath('.//div[@class="col-xs-12 col-sm-4 page-col"]/a')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for a in a_list:
                solu_url = urljoin(origion_url,a.xpath('./@href')[0])
                to_do.append(executor.submit(parse_solu,solu_url,firstTypeName))
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
    filename,dic = f'ACS解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')