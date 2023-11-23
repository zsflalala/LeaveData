import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'http://www.kaifull.net/solution/'    
    series_urls,firstTypeNames = [],[]
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//li[@class="case-li "]//div[@class="left"]/a')
    del a_list[-1],a_list[-1]
    for a in a_list:
        series_urls.append(a.xpath('./@href')[0])
        firstTypeNames.append(a.xpath('.//text()')[0].strip())
    for i in range(len(series_urls)):
        series_url = series_urls[i]
        firstTypeName = firstTypeNames[i]
        resp = requests.get(url=series_url,headers=headers)
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="gr-yyimg-list"]/li')
        for li in li_list:
            kind_url = li.xpath('./a/@href')[0]
            resp = requests.get(url=kind_url,headers=headers)
            resp.encoding = 'utf-8'
            tree = etree.HTML(resp.text)
            a_list = tree.xpath('.//ul[@class="com-yy-list clearfix"]//a')
            for a in a_list:
                pro_url = a.xpath('./@href')[0]
                pro_name = a.xpath('./text()')[0].strip()
                resp = requests.get(url=pro_url,headers=headers)
                resp.encoding = 'utf-8'
                tree = etree.HTML(resp.text)
                text = tree.xpath('.//div[@class="yy-content"]//text()')
                text = ''.join([item.strip() for item in text])
                img_list = []
                img_tree = tree.xpath('.//div[@class="yy-content"]//img')
                for img in img_tree:
                    img_list.append(img.xpath('./@src')[0])
                Description = [{'content':text,'type':'text'},{'content':img_list,'type':'img'}]
                solu_dic = {}
                solu_dic['FirstType'] = firstTypeName
                solu_dic['SecondType'] = ''
                solu_dic['SolutionUrl'] = pro_url
                solu_dic['SolutionHTML'] = resp.text.strip()
                solu_dic['SolutionJSON'] = ''
                solu_dic['SolutionName'] = pro_name
                solu_dic[pro_name] = Description
                solu_dic['ProductUrl'] = []
                final_dic['pro'].append(solu_dic)
                logger.info(f'爬取方案{len(final_dic["pro"])}/21条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'凯福科技解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')