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
    logger.success('control {}==>{}',title,times)
    return result

if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'Cookie':'control_csrf=fc8uXBFoKZ8B6LrY; __eetech_uid=1-dwxg8w8k-loc9r7z5; _fbp=fb.1.1698632202891.1323176497; exp_last_visit=1383529547; exp_stashid=%7B%22id%22%3A%2270873899319ff91dc406976a0fb3f1d39bf22726%22%2C%22dt%22%3A1698889547%7D; _gid=GA1.2.911264382.1699232574; exp_csrf_token=57286688847203f54c92a16c1049e0cdc821fda4; controlwelcome=set; cf_clearance=6Ym2FHSaHnNL_6nUxuqhcROJL5wdg2qYCH9sOmfitu8-1699239280-0-1-246ce663.cf91930f.2c3ddf2f-0.2.1699239280; __gads=ID=aff5745fbe57bcdf:T=1698632202:RT=1699240220:S=ALNI_MZ7TtiTJfI3ZqPAyrGoDqFyLaF8hQ; __gpi=UID=00000c79ab58e38f:T=1698632202:RT=1699240220:S=ALNI_MZHyjP07s99ILsjUjnxi6jsv_TPSw; exp_last_activity=1699240285; exp_tracker=%7B%220%22%3A%22technical-articles%22%2C%221%22%3A%22news%22%2C%222%22%3A%22latest%22%2C%223%22%3A%22news%22%2C%224%22%3A%22articles%22%2C%22token%22%3A%22ab108b23dc2cf78ccf4663cd6be7927f43c879075318be37f450396db21754b55642489fef069d7dd8360876e83293ee%22%7D; _ga=GA1.1.871014789.1698632202; _ga_JYP0BY5ZSV=GS1.1.1699235857.6.1.1699240357.60.0.0',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }
    
    url = 'https://www.isa.org/news-press-releases'
    resp = httpx.get(url=url,headers=headers)
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    urls = []
    a_list = tree.xpath('//div[@class="page-content"]//a')
    for a in a_list:
        urls.append(urljoin(url,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    xpath_list,time_xpath,needtime = ['.//article'],'.//ul[@class="infoList infoList--horizontal"]/li[1]/text()',True
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime))
        for future in concurrent.futures.as_completed(to_do):
            title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)

    filename,dic = f'isa{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
