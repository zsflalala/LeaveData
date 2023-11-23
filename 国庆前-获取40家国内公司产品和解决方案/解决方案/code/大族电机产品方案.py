import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


def get_prourls(url,headers):
    pro_urls = []
    tree = etree.HTML(requests.get(url=url,headers=headers).text)
    div_lists = tree.xpath('//div[@class="product-list"]/div/div[@class="box fl text-center relative"]')
    for div in div_lists:
        pro_url = urljoin(url,div.xpath('./div[3]//a/@href')[0])
        pro_urls.append(pro_url)
    return pro_urls

@logger.catch
def parse_solution(url,headers,firstTypeName):
    solu_list = []
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    tr_list = tree.xpath('.//div[@class="tr clean"]')
    for tr in tr_list:
        detail_url = urljoin(url,tr.xpath('.//a/@href')[0])
        detail_resp = requests.get(url=detail_url,headers=headers)
        detail_tree = etree.HTML(detail_resp.text)
        SolutionName = detail_tree.xpath('.//div[@class="title text-center"]/text()')[0]
        text = detail_tree.xpath('.//div[@class="content"]//text()')
        text = ''.join([item.strip() for item in text])
        text_dic = {'content':text,'type':'text'}
        imgs = []
        img_tree = detail_tree.xpath('.//div[@class="content"]//img')
        if img_tree != []:
            for img in img_tree:
                imgs.append(urljoin(detail_url,img.xpath('./@src')[0]))
        img_dic = {'content':imgs,'type':'img'}

        solu_dic = {}
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = ''
        solu_dic['SolutionUrl'] = detail_url
        solu_dic['SolutionHTML'] = detail_resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = SolutionName
        solu_dic[SolutionName] = []
        solu_dic[SolutionName].append(text_dic)
        solu_dic[SolutionName].append(img_dic)
        solu_dic['ProductUrl'] = get_prourls(detail_url,headers)
        solu_list.append(solu_dic)
    return solu_list

def get_solution(url,headers):
    final_dic = {'pro':[]}
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    div_list = tree.xpath('.//div[@class="category"]/div')
    solu_urls,solu_typeName = [],[]
    for div in div_list:
        solu_urls.append(urljoin(url,div.xpath('./a/@href')[0]))
        typeName = div.xpath('.//text()')
        typeName = ''.join([item.strip() for item in typeName])
        solu_typeName.append(typeName)
    assert len(solu_urls) == len(solu_typeName)
    for i in range(len(solu_urls)):
        url = solu_urls[i]
        firstType = solu_typeName[i]
        final_dic['pro'] += parse_solution(url,headers,firstType)
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    url = 'https://www.hansmotor.com/application/1/'
    final_dic = get_solution(url,headers)
    
    filename,dic = '大族电机解决方案18.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')