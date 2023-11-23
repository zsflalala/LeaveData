import re
import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    urls = []
    origion_url = 'https://www.autonicschina.cn/industry/index/C'
    resp = requests.get(url=origion_url,headers=headers)
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('//*[@id="lnb"]/div/ul/li[2]/div/div/ul/li[1]/ul[1]/li')
    for li in li_list:
        urls.append(urljoin(origion_url,li.xpath('./a/@href')[0]))
    
    for url in urls:
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        pro_url_tree = tree.xpath('.//ul[@class="list-wrap in-image industry-application"]')
        if pro_url_tree == []:
            continue
        li_list = pro_url_tree[0].xpath('./li')
        pro_urls = []
        for li in li_list:
            href = li.xpath('./a/@href')[0]
            number = re.findall('.view\((.*?),',href)[0]
            letter = re.findall(", '(.*?)'",href)[0]
            pro_urls.append(f'https://www.autonicschina.cn/industry/view/{letter}/{number}')
            page_tree = tree.xpath('//*[@id="pageing"]/a')
            if len(page_tree) > 1:
                for i in range(2,len(page_tree)+1):
                    pro_urls.append(f'https://www.autonicschina.cn/industry/view/{letter}/{number}?pageIndex={i}')
        for url in pro_urls:
            resp = requests.get(url=url,headers=headers)
            tree = etree.HTML(resp.text)
            FirstType = tree.xpath('//*[@id="viewForm"]/h2/text()')[0]
            firstTypeName = tree.xpath('//*[@id="viewForm"]/div[1]/div/div[1]/h4/text()')[0]
            ProductUrl = []
            li_list_tree = tree.xpath('.//ul[@class="list-wrap in-image series-list"]/li')
            if li_list_tree != []:
                for li in li_list_tree:
                    ProductUrl.append(urljoin(origion_url,li.xpath('./a/@href')[0]))
            Description = {}
            text = tree.xpath('.//div[@class="row ptb20"]//p//text()')
            text = ''.join([item.strip() for item in text])
            img_list = []
            img_tree = tree.xpath('.//ul[@class="thum-list"]//img')
            for img in img_tree:
                img_list.append(urljoin(origion_url,img.xpath('./@src')[0]))
            Description['方案描述'] = text
            Description['方案图片'] = img_list
            solu_dic = {}
            solu_dic['FirstType'] = FirstType
            solu_dic['SecondType'] = ''
            solu_dic['SolutionUrl'] = url
            solu_dic['SolutionHTML'] = resp.text.strip()
            solu_dic['SolutionJSON'] = ''
            solu_dic['SolutionName'] = firstTypeName
            solu_dic[firstTypeName] = Description
            solu_dic['ProductUrl'] = ProductUrl
            final_dic['pro'].append(solu_dic)
            logger.info(f'爬取方案{len(final_dic["pro"])}/246条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'奥托尼克斯解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')