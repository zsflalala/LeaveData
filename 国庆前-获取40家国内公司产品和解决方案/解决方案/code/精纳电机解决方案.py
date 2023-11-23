import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


def get_prourls(url,headers):
    pro_urls = []
    if url == 'https://www.kinavo.com/product/3.html':
        url = 'https://www.kinavo.com/product/9/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//a[@class="e_button-15 s_button1 btn btn-primary "]')
    for a in a_list:
        pro_urls.append(urljoin(url,a.xpath('./@href')[0]))
    return pro_urls

@logger.catch
def parse_solution(url,headers):
    solu_list = []
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_page_url = urljoin(url,tree.xpath('.//div[@class="e_container-1 s_layout"]/div//a/@href')[0])

    typeName = tree.xpath('.//div[@class="e_container-1 s_layout"]/div/p/text()')
    typeName = ''.join([item.strip() for item in typeName])
    text = tree.xpath('.//div[@class="e_container-1 s_layout"]/div/div//text()')
    text = ''.join([item.strip() for item in text])
    text_dic = {'content':text,'type':'text'}

    solu_dic = {}
    solu_dic['FirstType'] = typeName
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = typeName
    solu_dic[typeName] = []
    solu_dic[typeName].append(text_dic)
    solu_dic['ProductUrl'] = get_prourls(pro_page_url,headers)
    solu_list.append(solu_dic)
    return solu_list

def get_solution(url,headers):
    final_dic = {'pro':[]}
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    solu_urls = []
    div_list = tree.xpath('.//div[@class="p_list"]/div')
    for div in div_list:
        solu_urls.append(urljoin(url,div.xpath('.//a/@href')[0]))
    for i in range(len(solu_urls)):
        url = solu_urls[i]
        final_dic['pro'] += parse_solution(url,headers)
        logger.info(f'爬取{len(final_dic["pro"])}/{len(solu_urls)}条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    url = 'https://www.kinavo.com/application/1630864438606848000.html'
    final_dic = get_solution(url,headers)
    
    filename,dic = f'精纳电机解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')