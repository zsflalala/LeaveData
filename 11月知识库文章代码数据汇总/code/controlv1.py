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


@logger.catch
def get_page_source(url,title,xpath_list,time_xpath,needtime,author_path,needauthor):      
    content,html_content,images,times,author,next_url,isError = '','',[],'','',url,0
    try:
        resp = httpx.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
    except Exception as e:
        isError = 1
        logger.error(f'{e}: {url}')
        return author,title,content,html_content,images,times,next_url,isError
    if resp.status_code != 200:
        logger.error(f'RespError :{resp.status_code} , {url}')
        isError = 1
        return author,title,content,html_content,images,times,next_url,isError
    else:
        resp_text = remove_comments(resp.text)
        tree = etree.HTML(resp_text)
    try:
        if title == '':
            try:
                title = tree.xpath('.//title[1]/text()')[0].strip()
            except IndexError:
                try:
                    title = tree.xpath('.//h1[1]/text()')[0].strip()
                except:
                    logger.error(f'TitleError: {url}')
                    isError = 1
                    return author,title,content,html_content,images,times,next_url,isError
        # 解决文章发布时间
        if needtime:
            times = tree.xpath(time_xpath)
            times = ''.join([item.strip() for item in times if item.strip()])
        if needauthor:
            try:
                author = tree.xpath(author_path)
                author = ''.join([item.strip() for item in author if item.strip()])
            except:
                pass
        for xpath in xpath_list:
            img_tree = tree.xpath(xpath + '//img')
            for img in img_tree:
                if bool(img.xpath('./@src')) and urljoin(url,img.xpath('./@src')[0]) != url:
                    images.append(urljoin(url,img.xpath('./@src')[0]))
            text = tree.xpath(xpath+'//text()')
            text = '\n'.join([item for item in text])
            no_tag_list = ['//script','//style','//noscript','//iframe','//svg','//button']
            for no_tag in no_tag_list:
                no_tag_tree = tree.xpath(xpath+no_tag)
                for tag in no_tag_tree:
                    tag_text = tag.xpath('.//text()')
                    tag_text = ''.join([item for item in tag_text])
                    text = text.replace(tag_text,'')
            content += text
            html_content += unescape(etree.tostring(tree.xpath(xpath)[0],encoding='utf-8').decode())
        images = list(set(images))
        return author,title,content,html_content,images,times,next_url,isError
    except Exception as e:
        isError = 1
        logger.error(f'{e} : {url}')
        return author,title,content,html_content,images,times,next_url,isError
    
def form_data(author,title,content,html_content,images,times,next_url):
    result = {}
    result['author'] = author
    result['title'] = title
    result['content'] = content
    result['html'] = html_content
    result['images'] = images
    result['insert_time'] = str(datetime.datetime.now())
    result['pubtime'] = times
    result['url'] = next_url
    logger.success('control {}==>{}==>{}',title,times,author)
    return result

def getUrls(series_url,urls):
    resp = requests.get(url=series_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="post  px-4 md:px-0 md:w-full pb-4"]//a[1]')
    for a in a_list:
        urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    logger.info(f'Now Urls : {len(urls)}')
    return

def getPages(com_url,page_id,urls):
    url = com_url + f'P{page_id}/'
    resp = httpx.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="post  px-4 md:px-0 md:w-full pb-4"]//a[1]')
    if len(a_list) > 0:
        urls.append(url)
        return False
    else:
        return True

if __name__ == '__main__':
    logger.add('control.log')
    final_dic = {'pro':[]}
    headers = {
        'Cookie':'__eetech_uid=1-dwxg8w8k-loc9r7z5; _fbp=fb.1.1698632202891.1323176497; exp_last_visit=1383529547; exp_stashid=%7B%22id%22%3A%221378dde7fb77c07da78a2cf3a03ef152910c18b5%22%2C%22dt%22%3A1699952226%7D; _gid=GA1.2.866016859.1699952229; exp_csrf_token=471baa1eda5b2ce869ff9454d0a2d0819c708a74; __gads=ID=aff5745fbe57bcdf:T=1698632202:RT=1700012217:S=ALNI_MZ7TtiTJfI3ZqPAyrGoDqFyLaF8hQ; __gpi=UID=00000c79ab58e38f:T=1698632202:RT=1700012217:S=ALNI_MZHyjP07s99ILsjUjnxi6jsv_TPSw; cf_clearance=XrHDbkiqkwn5YktIWmeQiLiVnSKW_okD3ShIytriZoE-1700012218-0-1-eeb755.f84c7.e3a3c8e7-0.2.1700012218; exp_last_activity=1700012224; exp_tracker=%7B%220%22%3A%22articles%2FP1900%22%2C%221%22%3A%22articles%22%2C%222%22%3A%22articles%2FP1900%2FP19%22%2C%223%22%3A%22articles%2FP1900%22%2C%224%22%3A%22articles%22%2C%22token%22%3A%22b3041c40371b38cb96593bb48a7b9857065a3a013daf35903da9f1558b6df3dcd9f28b312ec17042b816b9254abd09c5%22%7D; _ga=GA1.1.871014789.1698632202; _ga_JYP0BY5ZSV=GS1.1.1700010208.11.1.1700012227.49.0.0',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }
    origion_url = 'https://control.com/latest/'
    series_urls = [origion_url,'https://control.com/articles/']
    flag,batch = 0,0
    # 判断页码最大能到达多少
    with ThreadPoolExecutor(max_workers=10) as executor: 
        for page_id in range(19,38000,19):
            to_do = []
            to_do.append(executor.submit(getPages,series_urls[0],page_id,series_urls))
            to_do.append(executor.submit(getPages,series_urls[1],page_id,series_urls))
            batch += 1
            if batch % 10 == 0:
                for future in concurrent.futures.as_completed(to_do):
                    isEmpty = future.result()
                    if not isEmpty:
                        logger.info(f'Now SeriesUrlLength : {len(series_urls)}')
                        pass
                    else:
                        flag = 1
            if flag:
                break
    # P2660 135  
    logger.info(f'Total SeriesUrl : {len(series_urls)}')

    urls = []
    with ThreadPoolExecutor(max_workers=10) as executor:      
        for series_url in series_urls:
            executor.submit(getUrls,series_url,urls)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')

    xpath_list,time_xpath,needtime = [f'.//div[@class="border-t-7 border-red-700 w-full bg-white lg:px-4 pt-5 pb-7"]/div[{i}]'for i in range(1,4)],'.//span[@class="text-xl w-full lg:w-auto pb-4 lg:pb-0 block lg:inline-block"]/text()',True
    author_xpath,needauthor = './/span[@class="text-xl w-full lg:w-auto pb-4 lg:pb-0 block lg:inline-block"]//a//text()',True
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime,author_xpath,needauthor))
        for future in concurrent.futures.as_completed(to_do):
            author,title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(author,title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)

    filename,dic = f'control{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
