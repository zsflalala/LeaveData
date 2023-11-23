import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    
    pro_urls = []
    url = 'https://www.kollmorgen.cn/zh-cn/solutions/%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//*[@id="block-koll-forest-content"]/div[2]/div[2]/div/div/div/div//a')
    for a in a_list:
        pro_urls.append(urljoin(url,a.xpath('./@href')[0]))
    pro_urls = list(set(pro_urls))
    for url in pro_urls:
        resp = requests.get(url=url,headers=headers)
        tree = etree.HTML(resp.text)
        FirstType = ''
        title = tree.xpath('.//h1/text()')[0]
        all_text = tree.xpath('.//main//text()')
        all_text = ''.join([item.strip() for item in all_text]).replace('\xa0','')
        img_list = []
        img_tree = tree.xpath('.//main//img')
        for img in img_tree:
            img_list.append(urljoin(url,img.xpath('./@src')[0]))
        Description,ProductUrl = [],[]
        Description.append({'content':all_text,'type':'text'})
        Description.append({'content':img_list,'type':'img'})

        productUrl_tree = tree.xpath('.//div[@class="grid size3"]//a')
        for productUrl in productUrl_tree:
            ProductUrl.append(urljoin(url,productUrl.xpath('./@href')[0]))
        ProductUrl = list(set(ProductUrl))

        solu_dic = {}
        solu_dic['FirstType'] = FirstType
        solu_dic['SecondType'] = ''
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text.strip()
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = title
        solu_dic[title] = Description
        solu_dic['ProductUrl'] = ProductUrl
        final_dic['pro'].append(solu_dic)
        logger.info(f'爬取方案{len(final_dic["pro"])}/{len(pro_urls)}条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'科尔摩根解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')