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
    title = tree.xpath('.//h3/text()')[0].strip()
    Description = []
    desp_text = tree.xpath('.//*[@id="com_intr"]/div/ul/table/tbody/tr[3]//text()')
    desp_text = ''.join([item.strip() for item in desp_text]).replace('\xa0','')
    
    img_list = []
    img_tree = tree.xpath('.//div[@id="meta_content"]//img')
    for img in img_tree:
        img_list.append(urljoin(solu_url,img.xpath('./@src')[0]))
    if bool(img_list):
        Description.append({'content':img_list,'type':'img'})
    table_tree = tree.xpath('.//*[@id="com_intr"]/div/ul/table/tbody/tr[3]//table')
    for table in table_tree:
        table_str = etree.tostring(table,encoding='utf-8').decode()
        Description.append({'content':table_str,'type':'table'})
        table_text = table.xpath('.//text()')
        table_text = ''.join([item.strip() for item in table_text])
        desp_text = desp_text.replace(table_text,'')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})

    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    return solu_dic

def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'http://www.difuss.com/news/?sid=591'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//*[@id="ab_left"]')[0].xpath('./li/a')
    for a in a_list:
        firstTypeName = a.xpath('./text()')[0].strip()
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        solu_urls = []
        pro_list = tree.xpath('.//ul[@class="news_con"]//a')
        for a in pro_list:
            solu_urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
        solu_urls = list(set(solu_urls))
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for solu_url in solu_urls:
                to_do.append(executor.submit(parse_solu,solu_url,firstTypeName))
            for future in concurrent.futures.as_completed(to_do):
                solu_dic = future.result()
                final_dic['pro'].append(solu_dic)
                logger.info(f'爬取方案{len(final_dic["pro"])}/21条数据')
    return final_dic

if __name__ == "__main__":
    logger.add('runtime.log',retention='1 day')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'德弗斯解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')