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
    isError = 0
    content,html_content,images,times,next_url = '','',[],'',url
    resp = httpx.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    resp_text = remove_comments(resp.text)
    if resp.status_code != 200:
        logger.error(f'RespError :{resp.status_code} , {url}')
        isError = 1
        return title,content,html_content,images,times,next_url,isError
    else:
        tree = etree.HTML(resp_text)
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
        times = tree.xpath(time_xpath)
        times = ''.join([item.strip() for item in times if item.strip()])

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

def getUrls(url,urls):
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.json()['html_items'])
    a_list = tree.xpath('.//div[@class="ue_post_blocks_image"]//a')
    for a in a_list:
        urls.append(urljoin(url,a.xpath('./@href')[0]))
    return

if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',    
    }
    urls = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(1,33):
            url = f'https://www.iaasiaonline.com/?ucfrontajaxaction=getfiltersdata&layoutid=20008&elid=37761d9&ucpage={i}&addelids=c2238a4'
            executor.submit(getUrls,url,urls)
        for i in range(1,256):
            url = f'https://www.iaasiaonline.com/?ucfrontajaxaction=getfiltersdata&layoutid=20008&elid=83afb02&ucpage={i}&addelids=783ae7b'
            executor.submit(getUrls,url,urls)
    
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    time_xpath,needtime = '',False
    xpath_list = ['.//article']
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime))
        for future in concurrent.futures.as_completed(to_do):
            title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)
        

    filename,dic = f'iaa{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')


