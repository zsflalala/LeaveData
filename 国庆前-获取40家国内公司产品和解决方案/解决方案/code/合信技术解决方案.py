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
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    title = tree.xpath('.//div[@class="commonweb clearfix  hidden-xs visible-md"]/h2/text()')[0].strip()
    desp_text = tree.xpath('.//div[@class="commonweb contentbox"]/div[2]//text()')
    desp_text = ''.join([item.strip() for item in desp_text if item.strip()]).replace('\xa0','')
    img_list = []
    img_tree = tree.xpath('.//div[@class="commonweb contentbox"]/div[2]//img')
    for img in img_tree:
        img_list.append(urljoin(solu_url,img.xpath('./@src')[0]))
    desp_text2 = tree.xpath('.//div[@class="commonweb contentbox"]/div[3]//text()')
    desp_text2 = ''.join([item.strip() for item in desp_text2 if item.strip()]).replace('\xa0','')
    img_list2 = []
    img_tree = tree.xpath('.//div[@class="commonweb contentbox"]/div[3]//img')
    for img in img_tree:
        img_list2.append(urljoin(solu_url,img.xpath('./@src')[0]))

    Description = []
    if desp_text != '':
        Description.append({'content':desp_text,'type':'text'})
    if img_list != []:
        Description.append({'content':img_list,'type':'img'})
    if desp_text2 != '':
        Description.append({'content':desp_text2,'type':'text'})
    if img_list2 != []:
        Description.append({'content':img_list2,'type':'img'})
    ProductUrl = []
    li_list = tree.xpath('.//ul[@class="product-list"]/li')
    for li in li_list:
        ProductUrl.append(urljoin(solu_url,li.xpath('./a/@href')[0]))
    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    return solu_dic

def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.co-trust.com/Programme/Robot/Robot_List.html'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//p[@class="hidden-xs visible-md clearfix"]/a')
    for a in a_list:
        firstTypeName = a.xpath('./text()')[0].strip()
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="product-list"]/li')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for li in li_list:
                solu_url = urljoin(origion_url,li.xpath('./a/@href')[0])
                to_do.append(executor.submit(parse_solu,solu_url,firstTypeName))
            for future in concurrent.futures.as_completed(to_do):
                solu_dic = future.result()
                final_dic['pro'].append(solu_dic)
                logger.info(f'爬取方案{len(final_dic["pro"])}/76条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'合信技术解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')