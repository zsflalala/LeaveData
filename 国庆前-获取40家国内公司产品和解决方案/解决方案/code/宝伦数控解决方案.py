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
    title = tree.xpath('.//h1[@class="e_title h1 p_headA"]/div[1]/text()')[0].strip()
    all_text = tree.xpath('.//div[@data-ename="资讯详细描述"]//text()')
    all_text = ''.join([item.strip() for item in all_text]).replace('\xa0','')
    img_list = []
    img_tree = tree.xpath('.//div[@data-ename="资讯详细描述"]//img')
    for img in img_tree:
        img_list.append(urljoin(solu_url,img.xpath('./@src')[0]))

    Description = []
    if all_text != '':
        Description.append({'content':all_text,'type':'text'})
    if img_list != []:
        Description.append({'content':img_list,'type':'img'})

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
    origion_url = 'http://www.power-land.com/news/19/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('//*[@id="c_portalResnav_main-15916701282697189"]/div/nav/ul/li[2]/ul/li')
    for li in li_list:
        firstTypeName = li.xpath('./h3/a/text()')[0].strip()
        ul_li_list = li.xpath('./ul/li')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for li in ul_li_list:
                solu_url = urljoin(origion_url,li.xpath('./h3/a/@href')[0])
                to_do.append(executor.submit(parse_solu,solu_url,firstTypeName))
            for future in concurrent.futures.as_completed(to_do):
                solu_dic = future.result()
                final_dic['pro'].append(solu_dic)
                logger.info(f'爬取方案{len(final_dic["pro"])}/22条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'宝伦数控解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')