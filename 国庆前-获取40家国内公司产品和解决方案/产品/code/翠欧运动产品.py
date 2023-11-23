import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from html import unescape
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def parse_propage(pro_url,firstTypeName='',secondTypeName=''):
    pro_dics = {'pro':[]}
    
    resp = requests.get(url=pro_url,headers=headers,timeout=(2,10))
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    tabView_list = tree.xpath('.//div[@class="tabView" or @class="tabView hideView" or @class="tabView  hideView"]')
    for tabView in tabView_list:
        try:
            pro_name,pro_img = '',[]
            Description,Feature,Parameter = [],[],[]
            pro_name = tabView.xpath('.//h1/text()')[0].strip() + tabView.xpath('.//h4/text()')[0].strip()
            img_tree = tabView.xpath('.//img')
            for img in img_tree:
                pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
                break
            # Description
            desp_text = tabView.xpath('.//text()')
            desp_text = ''.join([item.strip() for item in desp_text])
            table_list = []
            table_tree = tabView.xpath('.//table')
            for table in table_tree:
                table_text = table.xpath('.//text()')
                table_text = ''.join([item.strip() for item in table_text])
                desp_text.replace(table_text,'')
                table_str = etree.tostring(table,encoding='utf-8').decode()
                Description.append({'content':table_str,'type':'table'})
            if bool(desp_text):
                Description.append({'content':desp_text,'type':'text'})
            desp_img_list = []
            for img in tabView.xpath('.//img'):
                desp_img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
            if bool(desp_img_list):
                Description.append({'content':desp_img_list,'type':'img'})

            div_list = tree.xpath('.//div[@class="detail_other_message no_margin_left"]/div')
            for div in div_list:
                desp_text = div.xpath('.//text()')
                desp_text = ''.join([item.strip() for item in desp_text])
                Description.append(desp_text)

            pro_dic = {}
            pro_dic['ProductName'] = pro_name
            pro_dic['ProductImage'] = pro_img
            pro_dic['ProductUrl'] = pro_url
            pro_dic['ProductHTML'] = unescape(resp.text.strip())
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = firstTypeName
            pro_dic['SecondType'] = secondTypeName
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = Description
            pro_dic['ProductDetail']['Feature'] = Feature
            pro_dic['ProductDetail']['Parameter'] = Parameter
            pro_dics['pro'].append(pro_dic)
        except Exception as e:
            logger.error(f'{e}')
    return pro_dics

def triomotion(headers):
    final_dic = {'pro':[]}
    origion_url = 'http://www.triomotion.cn/?list_2/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    urls = []
    a_list = tree.xpath('//*[@id="mainmenu"]/ul/li[2]//a')
    for a in a_list:
        url = urljoin(origion_url,a.xpath('./@href')[0])
        if url.startswith('http://www.triomotion.cn/'):
            urls.append(url)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')

    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            future = executor.submit(parse_propage,url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dics = future.result()
            final_dic['pro'] += pro_dics['pro']
            logger.success(f'已爬取{len(final_dic["pro"])}条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'_cliid=yFKa8hQmPEXJT1Gy; _checkRespLvBrowser=true; _siteStatId=a574304b-f600-4663-a88a-61686ec8b479; _siteStatDay=20231013; _siteStatRedirectUv=redirectUv_11702593; _siteStatVisitorType=visitorType_11702593; _siteStatVisit=visit_11702593; _lastEnterDay=2023-10-13; _siteStatReVisit=reVisit_11702593; _reqArgs=; _pdDay_7367_100=20231013; _pdDay_7535_100=20231013; _pdDay_7377_100=20231013; _pdDay_7366_100=20231013; _pdDay_8902_100=20231013; _pdDay_8900_100=20231013; _pdDay_9325_100=20231013; _pdDay_9334_100=20231013; _siteStatVisitTime=1697186052229',
        'Referer':'https://www.a-m-c.cn/col.jsp?id=227',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    final_dic = triomotion(headers=headers)
    filename=f'翠欧运动产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    