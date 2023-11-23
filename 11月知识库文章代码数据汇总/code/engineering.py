import json
import httpx
import requests
import datetime
from loguru import logger
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def get_page_source(geturl,url):
    title,content,html_content,images,times,next_url,isError = '','','',[],'',url,0
    try:
        resp = httpx.get(url=geturl,headers=headers)
        data = resp.json()
        title = data['result']['posts'][0]['project']['title']
        times = data['result']['posts'][0]['created']
        content = data['result']['posts'][0]['body']
        html_content = content
        imageUrl = data['result']['posts'][0]['project']['imageUrl']
        if bool(imageUrl):
            images.append(imageUrl)
        if not bool(title) or not bool(times) or not bool(content):
            logger.warning(f'Warning : {geturl}')
        return title,content,html_content,images,times,next_url,isError
    except Exception as e:
        isError = 1
        logger.error(f'{e}: {url}')
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

def getUrls(url,param,data,urls):
    data["requests"][0]["params"] = param
    resp = requests.Session().post(url=url,headers=headers,json=data)
    json_data = resp.json()
    hits = json_data["results"][0].get('hits')
    for hit in hits:
        url = hit.get('url')
        objectID = hit.get('objectID')
        try:
            if bool(url) and bool(objectID):
                urls.append(url)
                objectIds.append(objectID)
        except:
            logger.error(f'NumsError : {url}')
    logger.success('got one json.')
    return

if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Referer':'https://www.engineering.com/',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    url = 'https://9m1oa4rjeo-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.19.1)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.51.1)%3B%20Vue%20(2.6.14)%3B%20Vue%20InstantSearch%20(4.8.5)%3B%20JS%20Helper%20(3.11.3)&x-algolia-api-key=3731af80fcfebbf65f9551ae1c066755&x-algolia-application-id=9M1OA4RJEO'
    data = '{"requests":[{"indexName":"Articles2","params":"facets=%5B%22Author%22%2C%22ParentType%22%2C%22category%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=18&maxValuesPerFacet=20&page=9&query=&tagFilters="}]}'
    data = json.loads(data)
    urls,objectIds = [],[]
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(0,57):
            try:
                param = f'facets=%5B%22Author%22%2C%22ParentType%22%2C%22category%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=18&maxValuesPerFacet=20&page={i}&query=&tagFilters='
                executor.submit(getUrls,url,param,data,urls)
            except Exception as e:
                logger.error(f'{e} : {i}')
    logger.info(f'{len(urls)}')
    assert len(urls) == len(objectIds)

    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for i in range(len(urls)):
            url,objectid = urls[i],objectIds[i]
            geturl = f'https://www.engineering.com/api/projects/{objectid}/posts?limit=10&sort=oldest&before=0&since=0'
            to_do.append(executor.submit(get_page_source,geturl,url))
        for future in concurrent.futures.as_completed(to_do):
            title,content,html_content,images,times,next_url,isError = future.result()
            if not isError:
                solu_dic = form_data(title,content,html_content,images,times,next_url)
                final_dic['pro'].append(solu_dic)

    filename,dic = f'engineering{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
