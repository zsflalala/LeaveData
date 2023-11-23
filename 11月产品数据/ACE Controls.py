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

def getType(tree,body_html):
    FirstType,SecondType = tree.xpath('.//span[@class="segment hl2"]/text()')[0].strip(),''
    body_html.append(unescape(etree.tostring(tree.xpath('.//span[@class="segment hl2"]')[0],encoding='utf-8').decode()))
    return FirstType,SecondType

def getParaFeat(tree,body_html):
    Parameter,Feature = [],[]
    text = tree.xpath('.//div[@class="pagerow tdh"]//text()')
    text = ''.join([item.strip() for item in text if item.strip()])
    Parameter.append({'content':text,'type':'text'})
    body_html.append(unescape(etree.tostring(tree.xpath('.//div[@class="pagerow tdh"]')[0],encoding='utf-8').decode()))
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
        img_url = urljoin(url,img.xpath('./@src')[0])
        if img_url != 'https://www.acecontrols.com/skin/frontend/ace/default/images/ace-logo.svg':
            ProductImage.append(img_url)
    if proimg_xpath != '' and not ProductImage:
        isError,ErrorName = 1,'ProductImgError'
        logger.error(f'{ErrorName}=>{url}')
        return link,ProductName,FirstType,SecondType,ProductImage,body_html,text_content,img_content,table_content,video_content,Parameter,Feature,doc,rar,source,url,isError,ErrorName
    try:
        for xpath in xpath_list:
            img_length,table_length,video_length = len(img_content),len(table_content),len(video_content)
            # 产品图片
            img_tree = tree.xpath(xpath + '//img')
            for img in img_tree:
                if bool(img.xpath('./@src')) and urljoin(url,img.xpath('./@src')[0]) != 'https://www.acecontrols.com/skin/frontend/ace/default/images/ace-logo.svg':
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


if __name__ == '__main__':
    link,source = 'https://www.acecontrols.com/us/products/motion-control.html','ACE Controls'
    logger.add(f'{source}.log')
    final_dic = {'pro':[]}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    url = 'https://www.acecontrols.com/us/products/automation-control/miniature-shock-absorbers.html'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//ul[@class="level3"]//a')
    urls = []
    for a in a_list:
        urls.append(urljoin(link,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')

    title_xpath,proimg_xpath = './/h1[1]//text()','.//div[@class="image category-image"]//img'
    xpath_list = [
        '//div[@class="pagerow__container"]/div[@class="pagerow__wrapper offset"]'
    ]
    needType,needParaFeat = 1,1
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
