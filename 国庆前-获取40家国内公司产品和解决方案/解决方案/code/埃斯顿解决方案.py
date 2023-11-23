import re
import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    series_urls = []
    origion_url = 'http://www.estun.com/?list_2/'
    resp = requests.get(url=origion_url,headers=headers)
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="col-lg-3 col-md-6"]/a')
    for a in a_list:
        series_urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    for url in series_urls:
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        title = tree.xpath('//*[@id="about"]/div/div[1]/h2/text()')[0]
        overview = tree.xpath('//*[@id="about"]/div/div[2]/div/div[1]/div/div/div/p/text()')[0].strip()
        auto_solu_url = urljoin(origion_url,tree.xpath('.//ul[@class="tab-menu"]/li[1]/a/@href')[0])
        resp = requests.get(url=auto_solu_url,headers=headers)
        tree = etree.HTML(resp.text)
        auto_solu_img_list = []
        auto_solu_img = tree.xpath('/html/body/div[3]/div/div[2]/div[1]//img')
        for img in auto_solu_img:
            auto_solu_img_list.append(urljoin(origion_url,img.xpath('./@src')[0]))
        digital_solu_img_list = []
        digital_solu_img = tree.xpath('/html/body/div[3]/div/div[2]/div[2]//img')
        for img in digital_solu_img:
            digital_solu_img_list.append(urljoin(origion_url,img.xpath('./@src')[0]))
        movie_url_list = []
        solu_movie_url = urljoin(origion_url,tree.xpath('/html/body/div[3]/div/ul/li[3]/a/@href')[0])
        resp = requests.get(url=solu_movie_url,headers=headers)
        tree = etree.HTML(resp.text)
        div_list = tree.xpath('.//div[@class="grid-item grid-item-width branding fashion graphic"]')
        for div in div_list:
            onclick = div.xpath('./@onclick')[0]
            movie_url = urljoin(origion_url,re.findall("='(.*?)'",onclick)[0])
            resp = requests.get(url=movie_url,headers=headers)
            tree = etree.HTML(resp.text)
            movie_url_list.append(urljoin(origion_url,tree.xpath('//*[@id="blog-details"]/div/div/div/div/div/article/p/video/@src')[0]))
        Description = {}
        Description['行业概述'] = overview
        Description['工艺自动化解决方案'] = auto_solu_img_list
        Description['产线数字化解决方案'] = digital_solu_img_list

        solu_dic = {}
        solu_dic['FirstType'] = ''
        solu_dic['SecondType'] = ''
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text.strip()
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = title
        solu_dic[title] = Description
        solu_dic['ProductUrl'] = movie_url_list
        final_dic['pro'].append(solu_dic)
        logger.info(f'爬取方案{len(final_dic["pro"])}/10条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'埃斯顿解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')