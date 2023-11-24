import json
import httpx
import requests
from lxml import etree
from loguru import logger
from html import unescape
from urllib.parse import urljoin
from w3lib.html import remove_comments
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def getType(tree,body_html):
    xpath = ''
    FirstType,SecondType = '',''
    if bool(xpath):
        body_html.append(unescape(etree.tostring(tree.xpath(xpath)[0],encoding='utf-8').decode()))
    return FirstType,SecondType

def getParaFeat(tree,body_html):
    Parameter,Feature = [],[]
    xpath = ''
    if bool(xpath):
        body_html.append(unescape(etree.tostring(tree.xpath(xpath)[0],encoding='utf-8').decode()))
    return Parameter,Feature

@logger.catch
def get_page_source(url,xpath_list,title_xpath,proimg_xpath,needType,needParaFeat):
    ProductName,FirstType,SecondType,ProductImage,body_html = '','','',[],[]
    text_content,img_content,table_content,video_content  = [],[],[],[]
    Parameter,Feature,doc,rar = [],[],[],[]
    isError,ErrorName = 0,''
    try:
        resp = httpx.get(url=url,headers=headers)
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
        FirstType,SecondType = getType(tree,body_html)
        if not FirstType and not SecondType:
            logger.warning(f'FisrTypeWarning|SecondTypeWarning=>{url}')
    if needParaFeat:
        Parameter,Feature = getParaFeat(tree,body_html)
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
        logger.warning(f'ProductImageWarning=>{url}')
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
            if bool(text) or (len(img_content) - img_length) or (len(table_content) - table_length) or (len(video_content) - video_length):
                text_content.append(text)
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


if __name__ == '__main__':
    link,source = 'https://www.kebamerica.com/blog/the-basics-of-motion-control-indexing/','KEB America'
    logger.add(f'{source}.log')
    final_dic = {'pro':[]}
    cookies = {
        '_lfa': 'LF1.1.ddadfe398cba10e2.1698220687691',
        '_gid': 'GA1.2.1400009335.1700795995',
        '_ga': 'GA1.1.886036144.1698220687',
        '_ga_PHZ8J9NFP1': 'GS1.1.1700795995.2.1.1700796097.0.0.0',
    }

    headers = {
        'authority': 'www.kebamerica.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        # 'cookie': '_lfa=LF1.1.ddadfe398cba10e2.1698220687691; _gid=GA1.2.1400009335.1700795995; _ga=GA1.1.886036144.1698220687; _ga_PHZ8J9NFP1=GS1.1.1700795995.2.1.1700796097.0.0.0',
        'origin': 'https://www.kebamerica.com',
        'referer': 'https://www.kebamerica.com/products/?fwp_product_categories=hmis%2Crouter%2Cindustrial-pcs%2Cembedded-controls%2Cethercat-i-o%2Csoftware%2Cdrives-sub%2Cregenerative-drives%2Cbraking-resistors%2Cbraking-transistor-monitor%2Cfilters-chokes%2Cdrive-panels%2Csoftware-drives%2Cintegral-gearmotors%2Cgearing%2Cmotors%2Cfeedback-cables%2Cbrakes%2Cclutches%2Crectifiers',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    params = {
        'fwp_product_categories': 'hmis,router,industrial-pcs,embedded-controls,ethercat-i-o,software,drives-sub,regenerative-drives,braking-resistors,braking-transistor-monitor,filters-chokes,drive-panels,software-drives,integral-gearmotors,gearing,motors,feedback-cables,brakes,clutches,rectifiers',
    }

    json_data = {
        'action': 'facetwp_refresh',
        'data': {
            'facets': {
                'product_categories': [
                    'hmis',
                    'router',
                    'industrial-pcs',
                    'embedded-controls',
                    'ethercat-i-o',
                    'software',
                    'drives-sub',
                    'regenerative-drives',
                    'braking-resistors',
                    'braking-transistor-monitor',
                    'filters-chokes',
                    'drive-panels',
                    'software-drives',
                    'integral-gearmotors',
                    'gearing',
                    'motors',
                    'feedback-cables',
                    'brakes',
                    'clutches',
                    'rectifiers',
                ],
                'load_more': [
                    4,
                ],
            },
            'frozen_facets': {},
            'http_params': {
                'get': {
                    'fwp_product_categories': 'hmis%2Crouter%2Cindustrial-pcs%2Cembedded-controls%2Cethercat-i-o%2Csoftware%2Cdrives-sub%2Cregenerative-drives%2Cbraking-resistors%2Cbraking-transistor-monitor%2Cfilters-chokes%2Cdrive-panels%2Csoftware-drives%2Cintegral-gearmotors%2Cgearing%2Cmotors%2Cfeedback-cables%2Cbrakes%2Cclutches%2Crectifiers',
                },
                'uri': 'products',
                'url_vars': {
                    'product_categories': [
                        'router',
                    ],
                },
            },
            'template': 'wp',
            'extras': {
                'sort': 'default',
            },
            'soft_refresh': 1,
            'is_bfcache': 1,
            'first_load': 0,
            'paged': 1,
        },
    }
    
    urls = []
    url = 'https://www.kebamerica.com/products/'
    for i in range(1,7):
        resp = requests.post(url=url, params=params, cookies=cookies, headers=headers, json=json_data)
        template = resp.json()['template']
        tree = etree.HTML(template)
        a_list = tree.xpath('.//div[@class="product-card p-3 md:h-full"]//a')
        for a in a_list:
            urls.append(urljoin(link,a.xpath('./@href')[0]))
        json_data['data']['paged'] = i + 1
    logger.info(len(urls))

    title_xpath,proimg_xpath = './/title/text()','.//div[@class="slider-nav flex flex-wrap mt-8"]//img'
    xpath_list = [
        '//*[@id="content"]'
    ]
    needType,needParaFeat = 0,0
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
