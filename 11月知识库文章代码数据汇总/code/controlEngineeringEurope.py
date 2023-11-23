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

def getUrls(origion_url,urls):
    post_url = origion_url
    last_number = 0
    for i in range(150):
        try:
            if i == 0:
                resp = requests.get(url=origion_url,headers=headers)
            else:
                if origion_url == 'https://www.controlengeurope.com/news.aspx':
                    post_url = origion_url
                elif i == 1:
                    post_url = origion_url + 'sid=0'
                else:
                    post_url += '&sid=0'
                resp = httpx.post(url=post_url,headers=headers,data=data)
            resp.encoding = 'utf-8'
            tree = etree.HTML(resp.text)
            a_list = tree.xpath('//*[@id="comments"]//a')
            for a in a_list:
                url = urljoin(origion_url,a.xpath('./@href')[0])
                if url.startswith('https://www.controlengeurope.com/') and url not in urls:
                    urls.append(url)
            __VIEWSTATE = tree.xpath('//*[@id="__VIEWSTATE"]/@value')
            __VIEWSTATEGENERATOR = tree.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')
            __EVENTVALIDATION = tree.xpath('//*[@id="__EVENTVALIDATION"]/@value')
            data = {
                '__EVENTTARGET':'ctl00$MainContent$rptArticles$ctl20$lbNext',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':__VIEWSTATE,
                '__VIEWSTATEGENERATOR':__VIEWSTATEGENERATOR,
                '__EVENTVALIDATION':__EVENTVALIDATION,
                'ctl00$txtSearch':''
            }
            logger.info(f'{origion_url} {i} have got data.UrlLength:{len(urls)}')
            if last_number == len(urls):
                logger.info(f'{origion_url} got full data in {i}')
                break
            else:
                last_number = len(urls)
        except httpx.ReadTimeout:
            logger.warning(f'httpx.ReadTimeout: {origion_url} break in {i}')
            break
        except Exception as e:
            logger.warning(f'{e}: {origion_url} break in {i}')
            break
    return

if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'Referer':'https://www.controlengeurope.com/case-studies/0/All/?sid=0',
        'Cookie':'_ga=GA1.1.1250010020.1699241105; ASP.NET_SessionId=o5y0e52ihmtm4yvg4id4nfnw; __utma=132011421.294996241.1699241105.1699256544.1699262993.3; __utmc=132011421; __utmz=132011421.1699262993.3.3.utmcsr=motiong.feishu.cn|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; __utmb=132011421.20.4.1699263045862; _ga_B803R1KKZY=GS1.1.1699262993.3.1.1699263095.0.0.0',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }
    origion_urls = [
        'https://www.controlengeurope.com/case-studies/0/All/?',
        'https://www.controlengeurope.com/features/0/All/?',
        'https://www.controlengeurope.com/news.aspx',
        'https://www.controlengeurope.com/products/0/All/?',
    ]
    urls = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for origion_url in origion_urls:
            executor.submit(getUrls,origion_url,urls)
    # for origion_url in origion_urls:
    #     getUrls(origion_url,urls)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')

    xpath_list,time_xpath,needtime = ['.//div[@class="portus-main-content portus-main-content-s-2"]'],'//*[@id="articledate"]/text()',True
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime))
        for future in concurrent.futures.as_completed(to_do):
            title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)

    filename,dic = f'controlEngineeringEurope{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
