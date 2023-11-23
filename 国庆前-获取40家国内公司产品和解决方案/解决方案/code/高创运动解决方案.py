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
    title = tree.xpath('.//div[@class="FaDet-show-title pb30 por color fs42"]/text()')[0].strip()
    all_text = tree.xpath('.//div[@class="FaDet-show-text fs18 lh36 fmL c5 mt30"]//text()')
    all_text = ''.join([item.strip() for item in all_text]).replace('\xa0','')
    img_list = []
    img_tree = tree.xpath('.//div[@class="FaDet-video-bg"]//img')
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

@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.servotronix.cn/bdt'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('/html/body/div[2]/div[2]/div/div[1]/a')
    for a in a_list:
        firstTypeName = a.xpath('./text()')[0].strip()
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="Fa-list"]/li')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for li in li_list:
                solu_url = urljoin(origion_url,li.xpath('./a/@href')[0])
                to_do.append(executor.submit(parse_solu,solu_url,firstTypeName))
            for future in concurrent.futures.as_completed(to_do):
                solu_dic = future.result()
                final_dic['pro'].append(solu_dic)
                logger.info(f'爬取方案{len(final_dic["pro"])}/29条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'高创运动解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')