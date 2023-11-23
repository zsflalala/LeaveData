import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from html import unescape
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def getUrls(cmsId,urls,origion_url):
    url = f'https://webapp-api.beckhoff.cn/navigation/navigation.proxy.php?callback=jQuery360022199661655486747_1699845528897&domain=www.beckhoff.com.cn&action=itemList&template=mobile&subtemplate=&cmsPreviewClient=false&cmsLanguage=&cmsNativeLanguage=ZH-CN&initCmsId=379&cmsId={cmsId}&cmsIdList=&cmsPid=219208&depth=&facet=&direction=&_=1699845528907'
    resp = requests.get(url=url,headers=headers)
    data = resp.text.replace('jQuery360022199661655486747_1699845528897(','').replace(')','')
    data = json.loads(data)
    tree = etree.HTML(data['view'])
    li_list = tree.xpath('.//li')
    data_cms_id = []
    for li in li_list:
        data_cms_id = li.xpath('.//button/@data-cms-id')[0]
        a = li.xpath('.//a/@href')[0]
        if a.endswith('.html'):
            urls.append(urljoin(origion_url,a))
        else:
            try:
                url = f'https://webapp-api.beckhoff.cn/navigation/navigation.proxy.php?callback=jQuery360022199661655486747_1699845528897&domain=www.beckhoff.com.cn&action=itemList&template=mobile&subtemplate=&cmsPreviewClient=false&cmsLanguage=&cmsNativeLanguage=ZH-CN&initCmsId=379&cmsId={data_cms_id}&cmsIdList=&cmsPid=219208&depth=&facet=&direction=&_=1699845528907'
                resp = requests.get(url=url,headers=headers)
                data = resp.text.replace('jQuery360022199661655486747_1699845528897(','').replace(')','')
                data = json.loads(data)
                tree = etree.HTML(data['view'])
                li_list2 = tree.xpath('.//li')
                for li2 in li_list2:
                    data_cms_id2 = li2.xpath('.//button/@data-cms-id')[0]
                    a2 = li2.xpath('.//a/@href')[0]
                    if a2.endswith('.html'):
                        urls.append(urljoin(origion_url,a2))
                    else:
                        try:
                            url = f'https://webapp-api.beckhoff.cn/navigation/navigation.proxy.php?callback=jQuery360022199661655486747_1699845528897&domain=www.beckhoff.com.cn&action=itemList&template=mobile&subtemplate=&cmsPreviewClient=false&cmsLanguage=&cmsNativeLanguage=ZH-CN&initCmsId=379&cmsId={data_cms_id2}&cmsIdList=&cmsPid=219208&depth=&facet=&direction=&_=1699845528907'
                            resp = requests.get(url=url,headers=headers)
                            data = resp.text.replace('jQuery360022199661655486747_1699845528897(','').replace(')','')
                            data = json.loads(data)
                            tree = etree.HTML(data['view'])
                            li_list3 = tree.xpath('.//li')
                            for li3 in li_list3:
                                data_cms_id3 = li3.xpath('.//button/@data-cms-id')[0]
                                a3 = li3.xpath('.//a/@href')[0]
                                if a3.endswith('.html'):
                                    urls.append(urljoin(origion_url,a3))
                                else:
                                    try:
                                        url = f'https://webapp-api.beckhoff.cn/navigation/navigation.proxy.php?callback=jQuery360022199661655486747_1699845528897&domain=www.beckhoff.com.cn&action=itemList&template=mobile&subtemplate=&cmsPreviewClient=false&cmsLanguage=&cmsNativeLanguage=ZH-CN&initCmsId=379&cmsId={data_cms_id3}&cmsIdList=&cmsPid=219208&depth=&facet=&direction=&_=1699845528907'
                                        resp = requests.get(url=url,headers=headers)
                                        data = resp.text.replace('jQuery360022199661655486747_1699845528897(','').replace(')','')
                                        data = json.loads(data)
                                        tree = etree.HTML(data['view'])
                                        li_list4 = tree.xpath('.//li')
                                        for li4 in li_list4:
                                            data_cms_id4 = li4.xpath('.//button/@data-cms-id')[0]
                                            a4 = li4.xpath('.//a/@href')[0]
                                            if a4.endswith('.html'):
                                                urls.append(urljoin(origion_url,a4))
                                            else:
                                                try:
                                                    url = f'https://webapp-api.beckhoff.cn/navigation/navigation.proxy.php?callback=jQuery360022199661655486747_1699845528897&domain=www.beckhoff.com.cn&action=itemList&template=mobile&subtemplate=&cmsPreviewClient=false&cmsLanguage=&cmsNativeLanguage=ZH-CN&initCmsId=379&cmsId={data_cms_id4}&cmsIdList=&cmsPid=219208&depth=&facet=&direction=&_=1699845528907'
                                                    resp = requests.get(url=url,headers=headers)
                                                    data = resp.text.replace('jQuery360022199661655486747_1699845528897(','').replace(')','')
                                                    data = json.loads(data)
                                                    tree = etree.HTML(data['view'])
                                                    li_list5 = tree.xpath('.//li')
                                                    for li5 in li_list5:
                                                        a5 = li5.xpath('.//a/@href')[0]
                                                        if a5.endswith('.html'):
                                                            urls.append(urljoin(origion_url,a5))
                                                        else:
                                                            logger.warning(f'4Warning : {urljoin(origion_url,a5)}')
                                                except Exception as e:
                                                    logger.warning(f'4Warning : {urljoin(origion_url,a4)}')
                                    except Exception as e:
                                        urls.append(urljoin(origion_url,a3))
                                        logger.warning(f'3Warning : {urljoin(origion_url,a3)}')
                        except Exception as e:
                            urls.append(urljoin(origion_url,a2))
                            logger.warning(f'2Warning : {urljoin(origion_url,a2)}')
            except Exception as e:
                logger.warning(f'1Warning : {urljoin(origion_url,a)}')

@logger.catch
def parse_propage(pro_url,firstTypeName='',secondTypeName=''):
    isError = 0
    pro_name,pro_img = '',[]
    Description,Feature,Parameter = [],[],[]
    try:
        resp = requests.get(url=pro_url,headers=headers,timeout=(2,10))
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        try:
            pro_name = tree.xpath('.//h1/text()')[0].strip()
        except IndexError:
            pro_name = tree.xpath('.//title/text()')[0].strip()
        except:
            isError = 1
            logger.error(f'NameError : {pro_url}')
            return {},isError
        
        img_tree = tree.xpath('.//figure[@class="figure figure-gallery-container"]//img')
        for img in img_tree:
            pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
        tag_list = tree.xpath('.//nav[@class="nav-breadcrumb"]//ol/li/a/text()')
        
        if len(tag_list) >= 3:
            for name in tag_list:
                if bool(name.strip()) and name != '首页' and name != 'breadcrumb' and name != '产品' :
                    firstTypeName = name
                    secondTypeName = tag_list[tag_list.index(name)+1]
                    break
        # Description
        desp_text = tree.xpath('.//main//text()')
        desp_text = ''.join([item.strip() for item in desp_text])
        for table in tree.xpath('.//main//table'):
            table_text = table.xpath('.//text()')
            table_text = ''.join([item.strip() for item in table_text])
            desp_text = desp_text.replace(table_text,'')
            table_str = etree.tostring(table,encoding='utf-8').decode()
            Parameter.append({'content':table_str,'type':'table'})
        if bool(desp_text):
            Description.append({'content':desp_text,'type':'text'})
    except Exception as e:
        isError = 1
        logger.error(f'{e} : {pro_url}')

    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = unescape(resp.text.strip())
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    if not bool(Description) and not bool(Parameter) and not bool(pro_name):
        isError = 1
    return pro_dic,isError

def Kinco():
    final_dic = {'pro':[]}
    cmsIds = [217169,216996,217171,217167,303340,292191]
    origion_url = 'https://www.beckhoff.com.cn/zh-cn/products/i-o/ethercat-terminals/ek1xxx-bk1xx0-ethercat-coupler/bk1120.html'
    urls = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for cmsId in cmsIds:
            executor.submit(getUrls,cmsId,urls,origion_url)
    urls = list(set(urls))
    logger.info(f'UrlLength {len(urls)}')
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url in urls:
            future = executor.submit(parse_propage,url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic,isError = future.result()
            if not isError:
               final_dic['pro'].append(pro_dic)
            logger.success(f'已爬取{len(final_dic["pro"])}/{len(urls)}条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'BeckhoffAutomationNavigation=gp0lcd8t0341mcfesehqdm78fk',
        'Referer':'https://www.beckhoff.com.cn/'
    }
    final_dic = Kinco()
    filename=f'倍福产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    