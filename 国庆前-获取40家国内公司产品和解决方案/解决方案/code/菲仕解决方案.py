import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def parse_solution(url,headers,firstTypeName):
    solu_list = []
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    typeName = tree.xpath('.//div[@class="main-title"]//text()')
    typeName = ''.join([item.strip() for item in typeName])
    text = tree.xpath('.//div[@class="box clearfix"]//text()')
    text = '.'.join([item.strip() for item in text])
    text_dic = {'content':text,'type':'text'}
    img = urljoin(url,tree.xpath('.//div[@class="box clearfix"]//img/@src')[0])
    img_dic = {'content':img,'type':'img'}

    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = typeName
    solu_dic[typeName] = []
    solu_dic[typeName].append(text_dic)
    solu_dic[typeName].append(img_dic)
    solu_dic['ProductUrl'] = ''
    solu_list.append(solu_dic)
    return solu_list

def get_solution(url,headers):
    final_dic = {'pro':[]}
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    solu_urls,firstTypeNames = [],[]
    li_list = tree.xpath('.//div[@class="auto auto_1280"]/ul[@class="ul clearfix"]/li')
    for li in li_list:
        solu_urls.append(urljoin(url,li.xpath('.//a/@href')[0]))
        firstTypeNames.append(li.xpath('.//h3/text()')[0])
    for i in range(len(solu_urls)):
        url = solu_urls[i]
        firstTypeName = firstTypeNames[i]
        final_dic['pro'] += parse_solution(url,headers,firstTypeName)
        logger.info(f'爬取解决方案{len(final_dic["pro"])}/{len(solu_urls)}条数据')
    return final_dic

@logger.catch
def parse_application(url,headers,firstTypeName):
    solu_list = []
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('.//ul[@class="nav ul"]//li')
    for li in li_list:
        app_url = urljoin(url,li.xpath('.//a/@href')[0])
        typeName = li.xpath('.//text()')
        typeName = ''.join([item.strip() for item in typeName])
        resp = requests.get(url=app_url,headers=headers)
        tree = etree.HTML(resp.text)
        ground_text = tree.xpath('.//div[@class="box_item box"]//p//text()')
        ground_text = '.'.join([item.strip() for item in ground_text])
        ground_text_dic = {'content':ground_text,'type':'text'}
        ground_img = urljoin(url,tree.xpath('.//div[@class="pic"]/img/@src')[0])
        ground_img_dic = {'content':ground_img,'type':'img'}
        overview = []
        overview_tree = tree.xpath('.//div[@class="box_item box1"]')
        if overview_tree != []:
            overview_text = overview_tree[0].xpath('.//p//text()')
            overview_text = '.'.join([item.strip() for item in overview_text])
            overview_text_dic = {'content':overview_text,'type':'text'}
            overview.append(overview_text_dic)
            overview_img_list = []
            overview_img_tree = overview_tree[0].xpath('.//img')
            if overview_img_tree != []:
                for img in overview_img_tree:
                    overview_img_list.append(urljoin(url,img.xpath('./@src')[0]))
                overview_img_dic = {'content':overview_img_list,'type':'img'}
                overview.append(overview_img_dic)
        advantage_text_list = []
        advantage_tree = tree.xpath('.//div[@class="box_item box2"]')
        if advantage_tree != []:
            li_list = advantage_tree[0].xpath('.//li')
            for li in li_list:
                advantage_text = li.xpath('.//text()')
                advantage_text = ''.join([item.strip() for item in advantage_text])
                advantage_text_list.append(advantage_text)
        ProductUrl = []
        product_tree = tree.xpath('.//div[@class="box_item box4"]')
        if product_tree != []:
            a_list = product_tree[0].xpath('.//a')
            for a in a_list:
                ProductUrl.append(urljoin(url,a.xpath('./@href')[0]))

        solu_dic = {}
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = ''
        solu_dic['SolutionUrl'] = app_url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = typeName
        solu_dic['背景介绍'] = [
            ground_text_dic,
            ground_img_dic
        ]
        solu_dic['方案概述'] = overview
        solu_dic['应用优势'] = advantage_text_list
        solu_dic['ProductUrl'] = ProductUrl
        solu_list.append(solu_dic)
    return solu_list

def get_application(url,headers):
    final_dic = {'pro':[]}
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    solu_urls,firstTypeNames = [],[]
    li_list = tree.xpath('.//ul[@class="data ul clearfix"]/li')
    for li in li_list:
        href_tree = li.xpath('.//a/@href')
        if(href_tree != []):
            solu_urls.append(urljoin(url,href_tree[0]))
            firstTypeNames.append(li.xpath('.//h3/text()')[0])
    for i in range(len(solu_urls)):
        url = solu_urls[i]
        firstTypeName = firstTypeNames[i]
        final_dic['pro'] += parse_application(url,headers,firstTypeName)
        logger.info(f'爬取行业应用{len(final_dic["pro"])}/25条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    url = 'http://www.physis.com.cn/Case/list.aspx'
    solution_dic = get_solution(url,headers)
    url = 'https://www.physis.com.cn/IndustryApplications/index.aspx?lcid=12&pid=12'
    application_dic = get_application(url,headers)
    solution_dic['pro'] += application_dic['pro']
    final_dic = solution_dic

    filename,dic = f'菲仕解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')