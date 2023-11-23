import json
import requests
from lxml import etree
from loguru import logger
from html import unescape
from urllib.parse import urljoin
from w3lib.html import remove_comments
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


@logger.catch
def parse_solu(solu_url,firstTypeName='',secondTypeName=''):
    title,isError = '',0
    ProductUrl,Description = [],[]
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(remove_comments(resp.text))
    title = tree.xpath('.//h1/text()')[0].strip()
    firstTypeName= tree.xpath('/html/body/div[1]/div[3]/div[1]/nav[2]/div/div/div/ol/li[3]/text()')[0].strip()

    desp_text = ''
    xpath_list = ['/html/body/div[1]/div[3]/main/div[3]','/html/body/div[1]/div[3]/main/div[4]','/html/body/div[1]/div[3]/main/div[5]']
    for xpath in xpath_list:
        text_tree = tree.xpath(xpath + '//text()')
        desp_text += ''.join([item.strip() for item in text_tree]).replace('\xa0','')
        no_tag_list = ['//script','//style','//noscript','//iframe','//svg','//button']
        for no_tag in no_tag_list:
            no_tag_tree = tree.xpath(xpath+no_tag)
            for tag in no_tag_tree:
                tag_text = tag.xpath('.//text()')
                tag_text = ''.join([item.strip() for item in tag_text])
                desp_text = desp_text.replace(tag_text,'')
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})

    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = secondTypeName
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = unescape(resp.text.strip())
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    return solu_dic,isError

def get_solution(headers):
    final_dic = {'pro':[]}
    urls = []
    origion_url = 'https://www.beckhoff.com.cn/zh-cn/navigation/flyout/industries/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//div[@class="dropdown__content"]//a')
    for a in a_list:
        urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(parse_solu,url))
        for future in concurrent.futures.as_completed(to_do):
            solu_dic,isError = future.result()
            if not isError:
                final_dic['pro'].append(solu_dic)
                logger.success(f'爬取方案{len(final_dic["pro"])}/{len(urls)}条数据')
            else:
                logger.error(f'Error : {solu_dic["SolutionUrl"]}')
    return final_dic

if __name__ == "__main__":
    logger.add('runtime.log',retention='1 day')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Cookie':'BeckhoffAutomationCMPCN=%7B%22matomo%22%3Atrue%2C%22dataprivacy%22%3Atrue%2C%22auth%22%3Atrue%7D; _pk_id.13.ae18=73949c85400e19ba.1698647374.; BeckhoffAutomationLanguage=en-au; ASP.NET_SessionId=itylbnar3ofylxl15msgjkmc; _pk_ref.13.ae18=%5B%22%22%2C%22%22%2C1699842143%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.13.ae18=1',
        'Referer':'https://www.beckhoff.com.cn/zh-cn/industries/automotive-industry/',

    }
    final_dic = get_solution(headers)
    filename,dic = f'倍福解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')