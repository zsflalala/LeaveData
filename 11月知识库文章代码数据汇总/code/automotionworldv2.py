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
def get_page_source(url,title,xpath_list,time_xpath,needtime):
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
        try:
            times = tree.xpath(time_xpath)
            times = ''.join([item.strip() for item in times if item.strip()])
        except:
            times = ''
            logger.warning(f'TimesWarning : {url}')
    # 作者
    try:
        author = tree.xpath('.//div[@class="author"]/span/a/text()')[0]
    except:
        author = ''
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
            break
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
            magazine_urls.append(f'https://www.automationworld.com/magazine/{id}')
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
    logger.add('automotionworldv2.log')
    final_dic = {'pro':[]}
    headers = {
        'authority': 'scorpia.graphql.aspire-ebm.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.automationworld.com',
        'referer': 'https://www.automationworld.com/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-tenant-key': 'ebm_automationworld',
    }
    json_data_magazine = {
        'query': "query getMagazineActiveIssues($publicationId: ObjectID!, $excludeIssueIds: [Int!], $limit: Int!) {\n  getMagazineActiveIssues(\n    input: {\n      requiresCoverImage: true\n      excludeIssueIds: $excludeIssueIds\n      publicationId: $publicationId\n      pagination: { limit: $limit }\n      sort: { field: mailDate, order: desc }\n    }\n  ) {\n    edges {\n      node {\n        id\n        name\n        description\n        mailed\n        credit\n        publication {\n          id\n          name\n          subscribeUrl\n          renewalUrl\n          reprintsUrl\n        }\n        digitalEditionUrl\n        coverImage {\n          src\n          alt\n          credit\n        }\n      }\n    }\n  }\n}\n",
        'variables': {
            'limit': 12,
            'excludeIssueIds': [
            ],
            'publicationId': '5d8a225ef6d5f267ee95d214',
        },
    }
    # magazines里面的文章 分两部分 开始界面get 之后用post
    urls,magazine_urls = [],[]
    url = 'https://www.automationworld.com/magazine/5d8a225ef6d5f267ee95d214'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="item"]//a')
    for a in a_list:
        magazine_urls.append(urljoin(url,a.xpath('./@href')[0]))
    logger.info('MagazineLength : {}',len(magazine_urls))
    # 获取magazine文章
    flag = 0
    while not flag:
        flag = getMagazineActiveIssuesUrls(json_data_magazine,magazine_urls)
    logger.info('MagazineLength : {}',len(magazine_urls))
    with ThreadPoolExecutor(max_workers=10) as executor:
        for magazine_url in magazine_urls:
            executor.submit(getMagzineUrls,magazine_url,urls)
    urls = list(set(urls))
    logger.info(f'MagazineUrls {len(urls)}')
    # 获取其他种类文章
    json_data_product = {
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
    
    json_data_factory = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'Document',
                'MediaGallery',
                'News',
                'Podcast',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 30001,
            'sectionId': 33182,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }

    json_data_process = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Article',
                'Blog',
                'Document',
                'MediaGallery',
                'News',
                'Podcast',
                'PressRelease',
                'Product',
                'Video',
                'Webinar',
                'Whitepaper',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 30001,
            'sectionId': 33189,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }

    json_data_podcast = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Podcast',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }

    json_data_supplier_news = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'scheduleOption': 30001,
            'sectionId': 63701,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }

    json_data_video = {
        'query': 'query getContentStream(\n  $sectionId: Int\n  $limit: Int\n  $skip: Int\n  $includeContentTypes: [ContentType!]\n  $issueId: Int\n  $relatedToId: Int\n  $authorId: Int\n  $scheduleOption: Int\n  $requirePrimaryImage: Boolean\n  $excludeContentIds: [Int!]\n  $includeContentIds: [Int!]\n  $sectionBubbling: Boolean\n  $sortField: ContentSortField\n  $sortOrder: SortOrder\n  $publishedBefore: Date\n  $publishedAfter: Date\n  $randomizeResults: Boolean\n  $teaserFallback: Boolean\n  $teaserMaxLength: Int\n  $startDateBefore: Date\n  $startDateAfter: Date\n) {\n  getContentStream(\n    input: {\n      sectionId: $sectionId\n      includeContentTypes: $includeContentTypes\n      excludeContentIds: $excludeContentIds\n      includeContentIds: $includeContentIds\n      issueId: $issueId\n      authorId: $authorId\n      relatedTo: { id: $relatedToId }\n      scheduleOption: $scheduleOption\n      startDateBefore: $startDateBefore\n      startDateAfter: $startDateAfter\n      requirePrimaryImage: $requirePrimaryImage\n      sectionBubbling: $sectionBubbling\n      publishedBefore: $publishedBefore\n      publishedAfter: $publishedAfter\n      sort: { field: $sortField, order: $sortOrder }\n      pagination: { limit: $limit, skip: $skip }\n      randomizeResults: $randomizeResults\n    }\n  ) {\n    edges {\n      node {\n        id\n        type\n        name\n        shortName\n        teaser(input: { useFallback: $teaserFallback, maxLength: $teaserMaxLength })\n        published\n        publishedDate\n        labels\n        primaryImage {\n          name\n          src\n          credit\n          alt\n          isLogo\n          displayName\n        }\n        primarySection {\n          alias\n          name\n        }\n        siteContext {\n          path\n        }\n        company {\n          id\n          name\n          fullName\n          alias\n        }\n        userRegistration {\n          isRequired\n          accessLevels\n        }\n        ... on Authorable {\n          authors {\n            edges {\n              node {\n                name\n                path\n              }\n            }\n          }\n        }\n        ... on ContentEvent {\n          startDate\n          endDate\n        }\n        ... on ContentWebinar {\n          startDate\n        }\n        membership {\n          id\n        }\n      }\n    }\n  }\n}\n',
        'variables': {
            'limit': 50,
            'excludeContentIds': [
            ],
            'sectionBubbling': True,
            'includeContentTypes': [
                'Video',
            ],
            'sortField': 'published',
            'sortOrder': 'desc',
            'requirePrimaryImage': False,
            'teaserFallback': True,
            'teaserMaxLength': 175,
        },
    }

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(getKindsUrls,json_data_product,urls,'Product')
        executor.submit(getKindsUrls,json_data_factory,urls,'Factory')
        executor.submit(getKindsUrls,json_data_process,urls,'Process')
        executor.submit(getKindsUrls,json_data_podcast,urls,'Podcast')
        executor.submit(getKindsUrls,json_data_supplier_news,urls,'SuperNews')
        executor.submit(getKindsUrls,json_data_video,urls,'Video')

    # webinars网页
    resp = requests.get(url='https://www.automationworld.com/webinars',headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@class="item small"]//a')
    for a in a_list:
        urls.append(urljoin(url,a.xpath('./@href')[0]))
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')  

    xpath_list = [
            '//div[@class="web-body-blocks page-contents__content-body"]//div[@class="html" or @class="text"]',
        ]
    time_xpath,needtime = './/div[@class="date-wrapper"]//text()',True
    count = 5
    while len(urls) and count:
        if count != 5:
            logger.info('===== deal time out urls {} =====',len(urls))
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for url in urls:
                to_do.append(executor.submit(get_page_source,url,'',xpath_list,time_xpath,needtime))
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
                elif ErrorName == 'RespError :301 ' or ErrorName == 'Invalidxpath':
                    del urls[urls.index(next_url)]
            count -= 1
            
    filename,dic = f'automotionworldv2_{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
