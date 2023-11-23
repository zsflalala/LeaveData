#encoding=utf-8
import json
import unicodedata
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
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cache-Control':'max-age=0',
        'Cookie':'_fbp=fb.1.1698219579399.847176128; oly_fire_id=2672C9123356A8B; oly_anon_id=07a9bb05-473e-433f-b52e-424130537c6d; cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _lo_uid=329262-1698219593530-51799ff744423539; __lotl=https%3A%2F%2Fwww.controleng.com%2Fresearch%2F; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; _gid=GA1.2.1261110125.1699236699; __lotr=https%3A%2F%2Fmotiong.feishu.cn%2F; TRINITY_USER_DATA=eyJ1c2VySWRUUyI6MTY5OTIzNjczMzUxOH0=; TRINITY_USER_ID=591f99aa-2c48-4c60-959e-3228f354376c; _lorid=329262-1699257507133-af0ad2c96441cdce; _lo_v=3; __gads=ID=af1c6a5c703a92cd:T=1699236700:RT=1699257819:S=ALNI_MbCz2PAxdz84HZluGCTgGK_5PV3QQ; __gpi=UID=00000c809f31a46f:T=1699236700:RT=1699257819:S=ALNI_MaBD69FsWuNkNefupOHamd46oqAHQ; nitroCachedPage=0; _ga_0K0DY08FJ8=GS1.1.1699257504.3.1.1699257836.41.0.0; _ga=GA1.1.199672704.1698219579',
        'If-Modified-Since':'Sun, 05 Nov 2023 23:48:42 GMT',
        'Sec-Ch-Ua':'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'none',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }
    series_urls = [
        'https://www.controleng.com/edge-cloud-computing/all/',
        'https://www.controleng.com/digital-transformation/all/',
        'https://www.controleng.com/control-systems/all/',
        'https://www.controleng.com/ai-machine-learning/all/',
    ]
    urls = []
    for url in series_urls:
        resp = requests.get(url=url,headers=headers,timeout=5)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//div[@class="postCard full-card" or @class="postCard full-card nitro-offscreen"]//a')
        for a in a_list:
            urls.append(urljoin(url,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    xpath_list,time_xpath,needtime = ['.//div[@class="singlePost singlePost--article "]'],'.//span[@class="singlePost__date"]/text()',True
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime))
        for future in concurrent.futures.as_completed(to_do):
            title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)

    filename,dic = f'controlEngering{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
