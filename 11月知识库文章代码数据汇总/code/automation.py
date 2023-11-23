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
def get_page_source(url,title,xpath_list,time_xpath,needtime):
    content,html_content,images,times,next_url,isError = '','',[],'',url,0
    try:
        resp = httpx.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
    except Exception as e:
        isError = 1
        logger.error(f'{e}: {url}')
        return title,content,html_content,images,times,next_url,isError
    if resp.status_code != 200:
        logger.error(f'RespError :{resp.status_code} , {url}')
        isError = 1
        return title,content,html_content,images,times,next_url,isError
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
                    return title,content,html_content,images,times,next_url,isError
        # 解决文章发布时间
        if needtime:
            times_tree = tree.xpath(time_xpath)
            for time in times_tree:
                if ',' in time:
                    times = time
                    break
        for xpath in xpath_list:
            img_tree = tree.xpath(xpath + '//img')
            for img in img_tree:
                if bool(img.xpath('./@src')) and urljoin(url,img.xpath('./@src')[0]) != url:
                    images.append(urljoin(url,img.xpath('./@src')[0]))
            text = tree.xpath(xpath+'//text()')
            text = ''.join([item.strip() for item in text])
            no_tag_list = ['//script','//style','//noscript','//iframe','//svg','//button']
            for no_tag in no_tag_list:
                no_tag_tree = tree.xpath(xpath+no_tag)
                for tag in no_tag_tree:
                    tag_text = tag.xpath('.//text()')
                    tag_text = ''.join([item.strip() for item in tag_text])
                    text = text.replace(tag_text,'')
            content += text
            html_content += unescape(etree.tostring(tree.xpath(xpath)[0],encoding='utf-8').decode())
        images = list(set(images))
        return title,content,html_content,images,times,next_url,isError
    except Exception as e:
        isError = 1
        logger.error(f'{e} : {url}')
        return title,content,html_content,images,times,next_url,isError
    
def form_data(title,content,html_content,images,times,next_url):
    result = {}
    result['author'] = ''
    result['title'] = title
    result['content'] = content
    result['html'] = html_content
    result['images'] = images
    result['insert_time'] = str(datetime.datetime.now())
    result['pubtime'] = times
    result['url'] = next_url
    logger.success('control {} {}',title,times)
    return result

def getUrls(series_url,urls):
    resp = requests.get(url=series_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//div[@class="twoCol-content js-observeResize"]//div[@class="contentSlab"]//a')
    for a in a_list:
        url = urljoin(series_url,a.xpath('./@href')[0])
        if url.startswith('https://www.automation.com/en-us'):
            urls.append(url)
    return

def getCateUrls(cate_url,series_urls):
    resp = requests.get(url=cate_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    series_url = urljoin(cate_url,tree.xpath('/html/body/div/main/main/section[2]/div/div/div[1]/div[4]/a/@href')[0])
    if series_url.startswith('https://www.automation.com/'):
        series_urls.append(series_url)
    return

if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',   
    }
    urls = []
    series_urls = [
        f'https://www.automation.com/en-us/smart-manufacturing-industry-4-0/articles-news-on-smart-manufacturing-industry-4-0?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/continuous-batch-processing/articles-news-on-continuous-batch-processing?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/operations-management/asset-management/articles-news-on-asset-management?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/discrete-manufacturing-machine-control/articles-news-on-discrete-mfg-machine-control?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/connectivity-cybersecurity/articles-news-on-connectivity-cybersecurity?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/industry-segments/articles-news-on-industry-segments?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/automation-news?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/news-by-company/international-society-automation-news-articles?listPage={i}'for i in range(1,21)
    ] + [
        f'https://www.automation.com/en-us/resources-list-pages/intech-articles?listPage={i}'for i in range(1,8)
    ]
    categories_url = 'https://www.automation.com/en-us/topic-categories'
    resp = requests.get(url=categories_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    cate_urls = []
    a_list = tree.xpath('//article//a')
    for a in a_list:
        cate_urls.append(urljoin(categories_url,a.xpath('./@href')[0]))
    cate_urls = list(set(cate_urls))
    logger.info(f'cateurls {len(cate_urls)}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        for cate_url in cate_urls:
            executor.submit(getCateUrls,cate_url,series_urls)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for series_url in series_urls:
            executor.submit(getUrls,series_url,urls)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    xpath_list,time_xpath,needtime = ['//article'],'.//ul[@class="infoList infoList--horizontal"]/li/text()',True
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime))
        for future in concurrent.futures.as_completed(to_do):
            title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)
    filename,dic = f'automation{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
