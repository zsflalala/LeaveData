import json
import httpx
import requests
import datetime
from lxml import etree
from loguru import logger
from html import unescape
from urllib.parse import urljoin
from w3lib.html import remove_comments
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def getType(tree):
    a_list = tree.xpath('.//div[@class="eStore_breadcrumb eStore_block980"]//a')
    if len(a_list) >= 3:
        FirstType,SecondType = a_list[1].xpath('./text()')[0].strip(),a_list[2].xpath('./text()')[0].strip()
    return FirstType,SecondType

def getParaFeat(tree):
    Parameter,Feature = [],[]
    return Parameter,Feature

@logger.catch
def get_page_source(url,xpath_list,title_xpath,proimg_xpath,needType,needParaFeat):
    ProductName,FirstType,SecondType,ProductImage,body_html = '','','',[],[]
    text_content,img_content,table_content,video_content  = [],[],[],[]
    Parameter,Feature,doc,rar = [],[],[],[]
    isError,ErrorName = 0,''
    try:
        resp = httpx.get(url=url,headers=headers,cookies=cookies)
        resp.encoding = 'utf-8'
    except Exception as e:
        isError,ErrorName = 1,str(e)
        logger.error(f'{ErrorName}=>{url}')
        return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    if resp.status_code != 200:
        isError,ErrorName = 1,'RespError'
        logger.error(f'{ErrorName}:{resp.status_code}=>{url}')
        return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    else:
        resp_text = remove_comments(resp.text)
        tree = etree.HTML(resp_text)
    if needType:
        FirstType,SecondType = getType(tree)
        if not FirstType and not SecondType:
            logger.warning(f'FisrTypeWarning|SecondTypeWarning=>{url}')
    if needParaFeat:
        Parameter,Feature = getParaFeat(tree)
        if not bool(Parameter) and not bool(Feature):
            logger.warning(f'ParameterWarning|FeatureWarning=>{url}')
    try:
        ProductName = tree.xpath(title_xpath)[0].strip()
    except:
        isError,ErrorName = 1,'TitleError'
        logger.error(f'{ErrorName}=>{url}')
        return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    
    for img in tree.xpath(proimg_xpath):
        ProductImage.append(urljoin(url,img.xpath('./@src')[0]))
    if proimg_xpath != '' and not ProductImage:
        for img in tree.xpath('.//div[@id="SingleImg"]/img'):
            ProductImage.append(urljoin(url,img.xpath('./@src')[0]))
        if not ProductImage:
            isError,ErrorName = 1,'ProductImgError'
            logger.error(f'{ErrorName}=>{url}')
            return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    try:
        for xpath in xpath_list:
            img_length,table_length,video_length = len(img_content),len(table_content),len(video_content)
            # 产品图片
            img_tree = tree.xpath(xpath + '//img')
            for img in img_tree:
                if bool(img.xpath('./@src')) and urljoin(url,img.xpath('./@src')[0]) != url:
                    img_content.append(urljoin(url,img.xpath('./@src')[0]))
            # 产品描述内容
            text = tree.xpath(xpath+'//text()')
            text = '\n'.join([item.strip() for item in text if item.strip()])
            # 表格
            for table in tree.xpath(xpath+'//div[@class="tab_table"]'):
                table_text = table.xpath('.//text()')
                table_text = '\n'.join([item.strip() for item in table_text if item.strip()])
                text = text.replace(table_text,'')
                table_str = etree.tostring(table,encoding='utf-8').decode()
                table_content.append(table_str)
            no_tag_list = ['//script','//style','//noscript','//iframe','//svg','//button']
            for no_tag in no_tag_list:
                no_tag_tree = tree.xpath(xpath+no_tag)
                for tag in no_tag_tree:
                    tag_text = tag.xpath('.//text()')
                    tag_text = '\n'.join([item.strip() for item in text if item.strip()])
                    text = text.replace(tag_text,'')
            # 视频
            for video in tree.xpath(xpath+'//video'):
                src = video.xpath('./@src')
                if bool(src):
                    video_content.append(urljoin(url,src[0]))
                else:
                    try:
                        video_content.append(urljoin(url,video.xpath('./source/@src')[0]))
                    except:
                        logger.warning(f'VideoWarning: {etree.tostring(video,encoding="utf-8").decode()}')
            for iframe in tree.xpath(xpath+'//iframe'):
                src = iframe.xpath('./@src')
                if bool(src) and 'youtube' in src[0]:
                    video_content.append(src[0])
            # doc and rar
            for a in tree.xpath(xpath + '//a'):
                href = a.xpath('./@href')
                if bool(href) and href[0].endswith('.pdf'):
                    doc.append(urljoin(link,href[0]))
                if bool(href) and href[0].endswith('.rar'):
                    rar.append(urljoin(link,href[0]))
            text_content.append(text)
            if bool(text) or (len(img_content) - img_length) or (len(table_content) - table_length) or (len(video_content) - video_length):
                body_html.append(unescape(etree.tostring(tree.xpath(xpath)[0],encoding='utf-8').decode()))
            else:
                logger.warning(f'XpathWarning-InvalidXpath: {xpath}=>{url}')
        img_content,table_content,video_content = list(set(img_content) - set(ProductImage)),list(set(table_content)),list(set(video_content))
        return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    except Exception as e:
        isError,ErrorName = 1,str(e)
        logger.error(f'{ErrorName}=>{url}')
        return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    
def form_data(link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url):
    dic_data = {
        'link': link,                                        # mangodb 的link
        'ProductName': ProductName,
        'FirstType':FirstType,
        'SecondType':SecondType,
        'ProductImage':ProductImage,
        'body_html': body_html,                              # 放所有参数文本和文本的html，如果没有或较难选中，就用源码
        'content': {                                         # content放产品参数，自由发挥，没有的就加......
            'Description':[
                {'content':text_content,'type':'text'},
                {'content':img_content,'type':'img'},
                {'content':table_content, 'type': 'table'},
                {'content':video_content, 'type': 'video'},
            ],
            'Parameter':Parameter,
            'Feature':Feature,
        },
        'doc': doc,
        'rar': rar,
        'video': [],                                         # 非产品参数的视频，一般为空
        'source': source,                                    # 关联产品和解决方案使用source公司名称
        'url': url,
    }
    return dic_data

def getUrls(url,params,urls):
    resp = requests.get(url=url,params=params,cookies=cookies,headers=headers)
    for product in resp.json():
        urls.append(urljoin(url,product['Url']))
    return

if __name__ == '__main__':
    link,source = 'https://buy.advantech.eu/Motion-Control-Cards/AEU_15751s.products.htm','Advantech'
    logger.add(f'{source}.log')
    final_dic = {'pro':[]}

    cookies = {
        'optimizelyEndUserId': 'oeu1697597666466r0.5770187153075134',
        '__zlcmid': '1IOmCiNuRUqxgbg',
        'LPVID': 'IzYzBkNWYwYThmMTgxOGUy',
        'CCPAAllowCookie': 'Allow',
        '_hjSessionUser_31101': 'eyJpZCI6IjdlODljNGRkLWI5MDItNWVhYy1hMDdiLTJkYTFhYmE5ODdiZSIsImNyZWF0ZWQiOjE2OTc1OTc2Njc2MDQsImV4aXN0aW5nIjp0cnVlfQ==',
        '_vwo_uuid_v2': 'D74F32AA55E3DD3E9C08194F3345E6D09|8152e86b032c2513d6374b21eff6b223',
        '_vwo_uuid': 'D74F32AA55E3DD3E9C08194F3345E6D09',
        '_ga_KZEZJERRNR': 'GS1.1.1697599934.1.0.1697599934.60.0.0',
        '_ga_7EYMYQDK8L': 'GS1.1.1698141717.1.0.1698141722.55.0.0',
        '_hjSessionUser_2448605': 'eyJpZCI6IjdkYzM5OTU2LWJkOTQtNTUxYi05M2NmLWNkMzUxNzYxODE1ZSIsImNyZWF0ZWQiOjE2OTgxOTU2Mzk1MjMsImV4aXN0aW5nIjp0cnVlfQ==',
        '_ga_LS3NMY5FLH': 'GS1.1.1698195613.1.1.1698196062.60.0.0',
        '_vis_opt_s': '4%7C',
        '_vwo_ds': '3%3At_0%2Ca_0%3A0%241697598938%3A14.53114518%3A%3A22_0%2C10_0%2C9_0%3A2_0%2C1_0%3A0',
        '_gid': 'GA1.2.1898417478.1700473389',
        '_fbp': 'fb.1.1700551677907.553084278',
        '_clck': 'etqcpa%7C2%7Cfgw%7C0%7C1386',
        'LPSID-30800048': 'gCLJpTH2SJOkkq0DdYLYKA',
        '_ga_8QDSXF1FD4': 'GS1.2.1700551676.8.1.1700552868.47.0.0',
        '_clsk': 'vjkb95%7C1700552869340%7C5%7C1%7Cz.clarity.ms%2Fcollect',
        '_ga_CFPK80LF7Y': 'GS1.1.1700551676.9.1.1700552901.14.0.0',
        'ASP.NET_SessionId': 'zioy42qmqnvci3sewiwz41em',
        'ASLBSA': '0003c8045b3468e354435925610325dac7e21949de9b1b7d69d4ff9eb7bf8bb751f0',
        'ASLBSACORS': '0003c8045b3468e354435925610325dac7e21949de9b1b7d69d4ff9eb7bf8bb751f0',
        '_ga': 'GA1.1.941436618.1697597667',
        'AdvTrackingCookieId': '3a55ea7b-4bc3-43f4-9a5f-24616d98423e',
        'AdvTrackingDeviceId': '839c5339b860b73c79141e867562f8ce',
        'isReturnCustomer': 'true',
        'eStore_category_displayModel': 'byPhoto',
        'tabSliceOut': '9999',
        '_ga_PZY6HV7LDY': 'GS1.1.1700619326.2.1.1700623088.47.0.0',
    }

    headers = {
        'authority': 'buysea.advantech.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'Cookie': 'optimizelyEndUserId=oeu1697597666466r0.5770187153075134; __zlcmid=1IOmCiNuRUqxgbg; LPVID=IzYzBkNWYwYThmMTgxOGUy; CCPAAllowCookie=Allow; _hjSessionUser_31101=eyJpZCI6IjdlODljNGRkLWI5MDItNWVhYy1hMDdiLTJkYTFhYmE5ODdiZSIsImNyZWF0ZWQiOjE2OTc1OTc2Njc2MDQsImV4aXN0aW5nIjp0cnVlfQ==; _vwo_uuid_v2=D74F32AA55E3DD3E9C08194F3345E6D09|8152e86b032c2513d6374b21eff6b223; _vwo_uuid=D74F32AA55E3DD3E9C08194F3345E6D09; _ga_KZEZJERRNR=GS1.1.1697599934.1.0.1697599934.60.0.0; _ga_7EYMYQDK8L=GS1.1.1698141717.1.0.1698141722.55.0.0; _hjSessionUser_2448605=eyJpZCI6IjdkYzM5OTU2LWJkOTQtNTUxYi05M2NmLWNkMzUxNzYxODE1ZSIsImNyZWF0ZWQiOjE2OTgxOTU2Mzk1MjMsImV4aXN0aW5nIjp0cnVlfQ==; _ga_LS3NMY5FLH=GS1.1.1698195613.1.1.1698196062.60.0.0; _vis_opt_s=4%7C; _vwo_ds=3%3At_0%2Ca_0%3A0%241697598938%3A14.53114518%3A%3A22_0%2C10_0%2C9_0%3A2_0%2C1_0%3A0; _gid=GA1.2.1898417478.1700473389; _fbp=fb.1.1700551677907.553084278; _clck=etqcpa%7C2%7Cfgw%7C0%7C1386; LPSID-30800048=gCLJpTH2SJOkkq0DdYLYKA; _ga_8QDSXF1FD4=GS1.2.1700551676.8.1.1700552868.47.0.0; _clsk=vjkb95%7C1700552869340%7C5%7C1%7Cz.clarity.ms%2Fcollect; _ga_CFPK80LF7Y=GS1.1.1700551676.9.1.1700552901.14.0.0; ASP.NET_SessionId=zioy42qmqnvci3sewiwz41em; ASLBSA=0003c8045b3468e354435925610325dac7e21949de9b1b7d69d4ff9eb7bf8bb751f0; ASLBSACORS=0003c8045b3468e354435925610325dac7e21949de9b1b7d69d4ff9eb7bf8bb751f0; _ga=GA1.1.941436618.1697597667; AdvTrackingCookieId=3a55ea7b-4bc3-43f4-9a5f-24616d98423e; AdvTrackingDeviceId=839c5339b860b73c79141e867562f8ce; isReturnCustomer=true; eStore_category_displayModel=byPhoto; tabSliceOut=9999; _ga_PZY6HV7LDY=GS1.1.1700619326.2.1.1700623932.57.0.0',
        'referer': 'https://buysea.advantech.com/I-O-Devices-Communication/SAP_31172.products.htm',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'page': '1',
        'pagesize': '72',
        'SortType': '',
        'filterType': '',
        'MatrixPage': 'false',
    }
    
    urls = []
    series_urls = {
        'https://buysea.advantech.com/api/Category/Products/SAP_31172':13,
        'https://buysea.advantech.com/api/Category/Products/SAP_17245s':8,
        'https://buysea.advantech.com/api/Category/Products/SAP_17243s':5,
        'https://buysea.advantech.com/api/Category/Products/SAP_17246s':5,
        'https://buysea.advantech.com/api/Category/Products/SAP_17247s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17248s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17086s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17094s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17112s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17113s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17111s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_31038s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17091s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_17130s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_31985s':2,
        'https://buysea.advantech.com/api/Category/Products/SAP_32079s':2,
    }
    with ThreadPoolExecutor(max_workers=15) as e:
        for url,endpage in series_urls.items():
            for i in range(1,13):
                e.submit(getUrls,url,params,urls)
                params['page'] = i + 1
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')

    title_xpath,proimg_xpath = './/title[1]/text()','.//div[@class="eStore_product_picSmall carouselBannerSingle"]//img'
    xpath_list = [
        './/div[@class="eStore_container eStore_block980"]'
    ]
    needType,needParaFeat = 1,0
    count = 3
    while len(urls) and count:
        if count != 3:
            logger.info('deal time out urls : {}',len(urls))
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for url in urls:
                to_do.append(executor.submit(get_page_source,url,xpath_list,title_xpath,proimg_xpath,needType,needParaFeat))
            for future in concurrent.futures.as_completed(to_do):
                link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName = future.result()
                if not isError:
                    if_product = 'true'
                    pro_dic = form_data(link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url)
                    final_dic['pro'].append(pro_dic)
                    del urls[urls.index(url)]
                    logger.success(f'one item have been saved in dic')
                elif ErrorName == 'The read operation timed out' or ErrorName == 'RespError':
                    pass
                else:
                    del urls[urls.index(url)]
        count -= 1

    filename,dic = f'{source}_{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
