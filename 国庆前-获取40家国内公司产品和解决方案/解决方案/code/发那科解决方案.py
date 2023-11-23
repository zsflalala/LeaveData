import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    urls = [
        'https://www.shanghai-fanuc.com.cn/applysolutions/',
        'https://www.shanghai-fanuc.com.cn/arcwelding/',
        'https://www.shanghai-fanuc.com.cn/friction/',
        'https://www.shanghai-fanuc.com.cn/assembly/',
        'https://www.shanghai-fanuc.com.cn/materiaprocess/',
        'https://www.shanghai-fanuc.com.cn/exohandling/',
        'https://www.shanghai-fanuc.com.cn/palletizing/',
        'https://www.shanghai-fanuc.com.cn/packaging/',
        'https://www.shanghai-fanuc.com.cn/loading/',
        'https://www.shanghai-fanuc.com.cn/painting/',
    ]
    for url in urls:
        resp = requests.get(url=url,headers=headers,verify=False)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        firstTypeName = tree.xpath('.//p[@class="wow slideInUp animated navgation"]/span[3]/a/text()')[0]
        Description = {}
        div_list = tree.xpath('.//div[@class="electronic"]')
        for div in div_list:
            title = div.xpath('.//p/text()')[0]
            text = div.xpath('.//div[@class="describe"]/text()')[0]
            Description[title] = text
        video_tree = tree.xpath('.//video')
        if video_tree != []:
            Description['相关视频'] = urljoin(url,video_tree[0].xpath('./@src')[0])
        ProductUrl = []
        div_list = tree.xpath('.//div[@class="robot"]')
        for div in div_list:
            a = div.xpath('.//a/@href')
            if len(a):
                ProductUrl.append(urljoin(url,a[0]))
        ProductUrl = list(set(ProductUrl))
        solu_dic = {}
        solu_dic['FirstType'] = ''
        solu_dic['SecondType'] = ''
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = firstTypeName
        solu_dic[firstTypeName] = Description
        solu_dic['ProductUrl'] = ProductUrl
        final_dic['pro'].append(solu_dic)
        logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.shanghai-fanuc.com.cn/homeindustry/'
    solu_urls,solu_names = [],[]
    resp = requests.get(url=url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('//*[@id="common-main"]/div/div[1]/div[1]/dl/div[2]/dd/ul/li')
    for li in li_list:
        solu_urls.append(urljoin(url,li.xpath('./a/@href')[0]))
        solu_names.append(li.xpath('./a/text()')[0])
    for i in range(len(solu_urls)):
        url = solu_urls[i]
        firstTypeName = solu_names[i]
        resp = requests.get(url=url,headers=headers,verify=False)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        Description = {}
        div_list = tree.xpath('.//div[@class="electronic"]/div')
        for div in div_list:
            title = div.xpath('.//p/text()')[0]
            text = div.xpath('.//div[@class="describe"]/text()')[0]
            Description[title] = text

        h4_tree = tree.xpath('.//h4/text()')
        if h4_tree != []:
            h4 = h4_tree[0]
            h4_text = tree.xpath('.//div[@class="apply-box"]//p/text()')
            h4_text = ''.join([item.strip() for item in h4_text])
            Description[h4] = h4_text
        div_list = tree.xpath('.//div[@class="swiper-slide"]')
        for div in div_list:
            try:
                name = div.xpath('.//p[@class="name"]/text()')[0]
                describes = div.xpath('.//p[@class="describes"]/text()')[0]
                img = urljoin(url,div.xpath('.//img/@src')[0])
                link_url_tree = div.xpath('.//a/@href')
                if link_url_tree != []:
                    link_url = urljoin(url,link_url_tree[0])
                else:
                    link_url = []
                Description[name] = [{'content':describes,'type':'text'},{'content':img,'type':'img'},{'content':link_url,'type':'url'}]
            except:
                pass
        video_tree = tree.xpath('.//video')
        if video_tree != []:
            Description['相关视频'] = urljoin(url,video_tree[0].xpath('./@src')[0])

        solu_dic = {}
        solu_dic['FirstType'] = ''
        solu_dic['SecondType'] = ''
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = firstTypeName
        solu_dic[firstTypeName] = Description
        solu_dic['ProductUrl'] = []
        final_dic['pro'].append(solu_dic)
        logger.info(f'爬取解决方案{i+1}/{len(solu_urls)}条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'发那科解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')