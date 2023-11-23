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
from fake_useragent import UserAgent


@logger.catch
def get_page_source(url,title,xpath_list,time_xpath,needtime,author_xpath,needauthor):
    author,content,html_content,images,times,next_url,isError,ErrorName = '','','',[],'',url,0,''
    try:
        resp = httpx.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
    except Exception as e:
        logger.error(f'{e}: {url}')
        isError,ErrorName = 1,str(e)
        return author,title,content,html_content,images,times,next_url,isError,ErrorName
    if resp.status_code != 200:
        logger.error(f'RespError :{resp.status_code} , {url}')
        isError,ErrorName = 1,'RespError'
        return author,title,content,html_content,images,times,next_url,isError,ErrorName
    else:
        resp_text = remove_comments(resp.text)
        tree = etree.HTML(resp_text)
    if title == '':
        try:
            title = tree.xpath('.//title[1]/text()')[0].strip()
        except IndexError:
            try:
                title = tree.xpath('.//h1[1]/text()')[0].strip()
            except:
                logger.error(f'TitleError: {url}')
                isError,ErrorName = 1,'TitleError'
                return author,title,content,html_content,images,times,next_url,isError,ErrorName
    # 解决文章发布时间
    if needtime:
        times = tree.xpath(time_xpath)
        times = ''.join([item.strip() for item in times if item.strip()])
    # 作者
    if needauthor:
        try:
            author = tree.xpath(author_xpath)
            author = ''.join([item.strip() for item in author if item.strip()])
        except:
            pass
    for xpath in xpath_list:
        dupi_flag = 0
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
        if text not in content:
            content += text
        else:
            dupi_flag = 1
        if bool(tree.xpath(xpath)) and not dupi_flag:
            html_content += unescape(etree.tostring(tree.xpath(xpath)[0],encoding='utf-8').decode())
    images = list(set(images))
    if bool(html_content) and bool(times):
        return author,title,content,html_content,images,times,next_url,isError,ErrorName
    else:
        logger.error(f'Invalidxpath : {url}')
        isError,ErrorName = 1,'Invalidxpath'
        return author,title,content,html_content,images,times,next_url,isError,ErrorName
    
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
    return result

def getMagzineUrls(magazine_url,urls):
    resp = requests.get(url=magazine_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('//div[@class="item small"]//a')
    for a in a_list:
        urls.append(urljoin(magazine_url,a.xpath('./@href')[0]))
    return

def getMagazineActiveIssuesUrls(json_data,magazine_urls):
    response = requests.post('https://scorpia.graphql.aspire-ebm.com/', headers=headers, json=json_data).json()
    edges = response['data']['getMagazineActiveIssues']['edges']
    if bool(edges):
        for edge in edges:
            id = edge['node']['id']
            magazine_urls.append(f'https://www.controlglobal.com/magazine/{id}')
            # logger.info(edge['node']['name'],'==> {}', edge['node']['id'])
            last_length = len(json_data['variables']['excludeIssueIds'])
            json_data['variables']['excludeIssueIds'].append(edge['node']['id'])
            json_data['variables']['excludeIssueIds'] = list(set(json_data['variables']['excludeIssueIds']))
            now_length = len(json_data['variables']['excludeIssueIds'])
            if last_length == now_length:
                flag = 1
                return True
        return False
    else:
        logger.warning(f'EdgesWarning : {edges}')
        return True

def getContentStreamUrls(json_data,urls):
    response = requests.post('https://scorpia.graphql.aspire-ebm.com/', headers=headers, json=json_data).json()
    edges = response['data']['getContentStream']['edges']
    if bool(edges):
        for edge in edges:
            edge_url = urljoin(url,edge['node']['siteContext']['path'])
            if edge_url not in urls:
                urls.append(edge_url)
            # logger.info('{} ==> {}',edge['node']['name'], edge['node']['id'])
            last_length = len(json_data['variables']['excludeContentIds'])
            json_data['variables']['excludeContentIds'].append(edge['node']['id'])
            json_data['variables']['excludeContentIds'] = list(set(json_data['variables']['excludeContentIds']))
            now_length = len(json_data['variables']['excludeContentIds'])
            if last_length == now_length:
                return True
        return False
    else:
        logger.warning(f'EdgesWarning : {edges}')
        return True

def getKindsUrls(json_data,urls,kind_name):
    flag = 0
    while not flag:
        flag = getContentStreamUrls(json_data,urls)
        logger.info('{} now url length : {}',kind_name,len(urls))
    logger.info('{} : {}',kind_name,len(urls))
    return

if __name__ == '__main__':
    logger.add('controlglobalv1.log')
    final_dic = {'pro':[]}
    headers = {
        'authority': 'scorpia.graphql.aspire-ebm.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.controlglobal.com',
        'referer': 'https://www.controlglobal.com/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-tenant-key': 'ebm_controlglobal',
    }
    urls = []
    json_data_magazine = {
        'query': 'query getMagazineActiveIssues($publicationId: ObjectID!, $excludeIssueIds: [Int!], $limit: Int!) {\n  getMagazineActiveIssues(\n    input: {\n      requiresCoverImage: true\n      excludeIssueIds: $excludeIssueIds\n      publicationId: $publicationId\n      pagination: { limit: $limit }\n      sort: { field: mailDate, order: desc }\n    }\n  ) {\n    edges {\n      node {\n        id\n        name\n        description\n        mailed\n        credit\n        publication {\n          id\n          name\n          subscribeUrl\n          renewalUrl\n          reprintsUrl\n        }\n        digitalEditionUrl\n        coverImage {\n          src\n          alt\n          credit\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 12,
            'excludeIssueIds': [
            ],
            'publicationId': '62bce21dedb4b7ac008b4569',
        },
    }
    # magazines里面的文章,先get请求,后post请求
    magazine_urls = []
    url = 'https://www.controlglobal.com/magazine/62bce21dedb4b7ac008b4569'
    # resp = requests.get(url=url,headers=headers)
    # resp.encoding = 'utf-8'
    # tree = etree.HTML(resp.text)
    # a_list = tree.xpath('.//div[@class="item"]//a')
    # for a in a_list:
    #     magazine_urls.append(urljoin(url,a.xpath('./@href')[0]))
    # logger.info('MagazineLength : {}',len(magazine_urls))
    # # 获取magazine文章
    # flag = 0
    # while not flag:
    #     flag = getMagazineActiveIssuesUrls(json_data_magazine,magazine_urls)
    # logger.info('MagazineLength : {}',len(magazine_urls))
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     for magazine_url in magazine_urls:
    #         executor.submit(getMagzineUrls,magazine_url,urls)
    # urls = list(set(urls))
    # logger.info(f'MagazineUrls {len(urls)}')

    json_data_calibration = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57932,
        },
    }
    # getKindsUrls(json_data_calibration,urls,'Calibration')
    json_data_flow = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57752,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_flow,urls,'Flow')
    json_data_level = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57758,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_level,urls,'level')
    json_data_pressure = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57879,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_pressure,urls,'pressure')
    json_data_temperature = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57759,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_temperature,urls,'temperature')
    json_data_vibration = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58056,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_vibration,urls,'vibration')
    json_data_weight = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58057,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_weight,urls,'weight')
    json_data_analyzers = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57878,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_analyzers,urls,'analyzers')
    json_data_loop_control = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57949,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_loop_control,urls,'loop-control')
    json_data_plcs_pacs = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57842,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_plcs_pacs,urls,'plcs_pacs')
    json_data_scada = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57903,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_scada,urls,'scada')
    json_data_multivariable_control = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58005,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_multivariable_control,urls,'json_data_multivariable_control')
    json_data_industrial_computers = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57940,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_industrial_computers,urls,'json_data_industrial_computers')
    json_data_actuators = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58018,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_actuators,urls,'json_data_actuators')
    json_data_drives = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57870,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_drives,urls,'json_data_drives')
    json_data_hmi = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57785,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_hmi,urls,'json_data_hmi')
    json_data_operator_interface = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58080,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_operator_interface,urls,'json_data_operator_interface')
    json_data_alarm_management = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57998,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_alarm_management,urls,'json_data_alarm_management')
    json_data_recorders = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58069,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_recorders,urls,'json_data_recorders')
    json_data_actuators = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58018,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_actuators,urls,'json_data_actuators')
    json_data_data_acquisition = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57798,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_data_acquisition,urls,'json_data_data_acquisition')
    json_data_mobile_access = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57966,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_mobile_access,urls,'json_data_mobile_access')
    json_data_wireless = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57786,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_wireless,urls,'json_data_wireless')
    json_data_industrial_networks = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57774,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_industrial_networks,urls,'json_data_industrial_networks')
    json_data_iosystems = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57874,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_iosystems,urls,'json_data_iosystems')
    json_data_powersupplies = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57994,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_powersupplies,urls,'json_data_powersupplies')
    json_data_remoteaccess = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57841,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_remoteaccess,urls,'json_data_remoteaccess')
    json_data_systemsintegration = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57777,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_systemsintegration,urls,'json_data_systemsintegration')
    json_data_assetmanagement = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57790,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_assetmanagement,urls,'json_data_assetmanagement')
    json_data_batchmanagement = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57969,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_batchmanagement,urls,'json_data_batchmanagement')
    json_data_optimization = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57762,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_optimization,urls,'json_data_optimization')
    json_data_dataanalytics = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57788,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_dataanalytics,urls,'json_data_dataanalytics')
    json_data_safety_instrumented_systems = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57819,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_safety_instrumented_systems,urls,'json_data_safety_instrumented_systems')
    json_data_intrinsic_safety = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58071,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_intrinsic_safety,urls,'json_data_intrinsic_safety')
    json_data_cybersecurity = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57840,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_cybersecurity,urls,'json_data_cybersecurity')
    json_data_physicalsecurity = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 58059,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_physicalsecurity,urls,'json_data_physicalsecurity')
    json_data_enclosures = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57952,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_enclosures,urls,'json_data_enclosures')
    json_data_podcasts = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57750,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_podcasts,urls,'json_data_podcasts')
    json_data_products = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Product',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_products,urls,'json_data_products')
    json_data_aiml = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57800,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_aiml,urls,'json_data_aiml')
    json_data_motors = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57871,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_motors,urls,'json_data_motors')
    json_data_valves = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'MediaGallery',
                'News',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
                'Promotion',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 2,
            'sectionId': 57836,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }
    # getKindsUrls(json_data_valves,urls,'json_data_valves')

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(getKindsUrls,json_data_calibration,urls,'json_data_calibration')
        executor.submit(getKindsUrls,json_data_flow,urls,'json_data_flow')
        executor.submit(getKindsUrls,json_data_level,urls,'json_data_level')
        executor.submit(getKindsUrls,json_data_pressure,urls,'json_data_pressure')
        executor.submit(getKindsUrls,json_data_temperature,urls,'json_data_temperature')
        executor.submit(getKindsUrls,json_data_vibration,urls,'json_data_vibration')
        executor.submit(getKindsUrls,json_data_weight,urls,'json_data_weight')
        executor.submit(getKindsUrls,json_data_analyzers,urls,'json_data_analyzers')
        executor.submit(getKindsUrls,json_data_loop_control,urls,'json_data_loop_control')
        executor.submit(getKindsUrls,json_data_plcs_pacs,urls,'json_data_plcs_pacs')
        executor.submit(getKindsUrls,json_data_scada,urls,'json_data_scada')
        executor.submit(getKindsUrls,json_data_multivariable_control,urls,'json_data_multivariable_control')
        executor.submit(getKindsUrls,json_data_industrial_computers,urls,'json_data_industrial_computers')
        executor.submit(getKindsUrls,json_data_actuators,urls,'json_data_actuators')
        executor.submit(getKindsUrls,json_data_drives,urls,'json_data_drives')
        executor.submit(getKindsUrls,json_data_hmi,urls,'json_data_hmi')
        executor.submit(getKindsUrls,json_data_alarm_management,urls,'json_data_alarm_management')
        executor.submit(getKindsUrls,json_data_recorders,urls,'json_data_recorders')
        executor.submit(getKindsUrls,json_data_data_acquisition,urls,'json_data_data_acquisition')
        executor.submit(getKindsUrls,json_data_mobile_access,urls,'json_data_mobile_access')
        executor.submit(getKindsUrls,json_data_wireless,urls,'json_data_wireless')
        executor.submit(getKindsUrls,json_data_industrial_networks,urls,'json_data_industrial_networks')
        executor.submit(getKindsUrls,json_data_iosystems,urls,'json_data_iosystems')
        executor.submit(getKindsUrls,json_data_powersupplies,urls,'json_data_powersupplies')
        executor.submit(getKindsUrls,json_data_remoteaccess,urls,'json_data_remoteaccess')
        executor.submit(getKindsUrls,json_data_systemsintegration,urls,'json_data_systemsintegration')
        executor.submit(getKindsUrls,json_data_assetmanagement,urls,'json_data_assetmanagement')
        executor.submit(getKindsUrls,json_data_batchmanagement,urls,'json_data_batchmanagement')
        executor.submit(getKindsUrls,json_data_optimization,urls,'json_data_optimization')
        executor.submit(getKindsUrls,json_data_safety_instrumented_systems,urls,'json_data_safety_instrumented_systems')
        executor.submit(getKindsUrls,json_data_intrinsic_safety,urls,'json_data_intrinsic_safety')
        executor.submit(getKindsUrls,json_data_cybersecurity,urls,'json_data_cybersecurity')
        executor.submit(getKindsUrls,json_data_physicalsecurity,urls,'json_data_physicalsecurity')
        executor.submit(getKindsUrls,json_data_podcasts,urls,'json_data_podcasts')
        executor.submit(getKindsUrls,json_data_products,urls,'json_data_products')
        executor.submit(getKindsUrls,json_data_aiml,urls,'json_data_aiml')
        executor.submit(getKindsUrls,json_data_motors,urls,'json_data_motors')
        executor.submit(getKindsUrls,json_data_valves,urls,'json_data_valves')

    for other_url in ['https://www.controlglobal.com/webinars','https://www.controlglobal.com/whitepapers']:
        resp = requests.get(url=other_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('//div[@class="item small"]//a')
        for a in a_list:
            urls.append(urljoin(url,a.xpath('./@href')[0]))
        urls = list(set(urls))
        logger.info(f'UrlLength {len(urls)}')
    
    xpath_list = [
            '//div[@class="web-body-blocks page-contents__content-body"]//div[@class="html" or @class="text" or @class="ssr-body"]',
        ]
    time_xpath,needtime,author_xpath,needauthor = '//div[@class="date-wrapper"]//text()',True,'.//div[@class="author"]//text()',True

    count = 5
    while len(urls) and count:
        if count != 5:
            logger.info('===== deal time out urls {} =====',len(urls))
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for url in urls:
                to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime,author_xpath,needauthor))
            for future in concurrent.futures.as_completed(to_do):
                author,title,content,html_content,images,times,next_url,isError,ErrorName = future.result()
                if not isError:
                    try:
                        del urls[urls.index(next_url)]
                        solu_dic = form_data(author,title,content,html_content,images,times,next_url)
                        final_dic['pro'].append(solu_dic)
                        logger.success('{}==>{}',title,times)
                    except:
                        logger.warning(f'NoUrlsWarning : {next_url}')
                elif ErrorName == 'RespError :301' or ErrorName == 'Invalidxpath':
                    del urls[urls.index(next_url)]
            count -= 1
    
    filename,dic = f'controlglobalv2_{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
