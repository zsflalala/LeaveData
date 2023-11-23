import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def get_prourl(series_url,headers):
    ProductUrl = []
    resp = requests.get(url=series_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    div_list = tree.xpath('.//div[@class="teaserbox__elementWrapper swiper-wrapper"]/div')
    for div in div_list:
        kind_url = urljoin(series_url,div.xpath('./a/@href')[0])
        resp = requests.get(url=kind_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="search__resultList resultList--product results-list"]/li')
        for li in li_list:
            ProductUrl.append(urljoin(series_url,li.xpath('./div/div[1]//a/@href')[0]))
    if ProductUrl == []:
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="search__resultList resultList--product results-list"]/li')
        for li in li_list:
            ProductUrl.append(urljoin(series_url,li.xpath('.//div[@class="product__summary"]/a/@href')[0]))
    return ProductUrl

def parse_solupage(origion_url,div,FirstType):
    solu_url = urljoin(origion_url,div.xpath('.//a/@href')[0])
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    title = tree.xpath('.//h1[@class="headline headline--h1 headline--center"]/text()')[0].strip()
    Description = {}
    text1 = tree.xpath('.//p[@class="headline headline--h4 headline--semiBold align-center"]/text()')[0].strip()
    text2 = tree.xpath('.//div[@class="frame frame-type-gridelements_pi1 frame-gridelement-2 backgroundColor--white"]//text()')
    text2 = ''.join([item.strip() for item in text2])
    text = text1 + text2
    text_dic = {'content':text,'type':'text'}
    img_list = []
    img_tree = tree.xpath('.//div[@class="textmedia textmedia--noText "]//img')
    for img in img_tree:
        img_list.append(urljoin(origion_url,img.xpath('./@src')[0]))
    img_dic = {'content':img_list,'type':'img'}
    Description['方案描述'] = [text_dic,img_dic]
    advantage = tree.xpath('.//div[@class="productAdvantage__text"]/text()')
    Description['方案优势'] = advantage
    ProductUrl = []
    a_list = tree.xpath('.//div[@class="swiper-wrapper recommendationModule__elementWrapper"]/a')
    for a in a_list:
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        ProductUrl += get_prourl(series_url,headers)
    solu_dic = {}
    solu_dic['FirstType'] = FirstType
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    return solu_dic

@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://faulhaber.com.cn/'
    series_urls,FirstTypes = [],[]
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//*[@id="54815"]/div/div/div//a')
    for a in a_list:
        series_urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
        FirstTypes.append(a.xpath('.//p[@class="teaserSliderElement__contentHeadline"]/text()')[0].strip())
    for i in range(len(series_urls)):
        series,FirstType = series_urls[i],FirstTypes[i]
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        div_list = tree.xpath('.//div[@class="teaserSlider teaserSlider--darkblue  Background js-slider"]/div/div[1]/div')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for div in div_list:
                future = executor.submit(parse_solupage,origion_url,div,FirstType) 
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                solu_dic = future.result()
                final_dic['pro'].append(solu_dic)
                logger.info(f'爬取方案{len(final_dic["pro"])}/35条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'福尔哈贝解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')