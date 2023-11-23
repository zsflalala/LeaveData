import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_page(product,final_dic,headers,firstTypeName,secondTypeName):
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    seriesSn = product['seriesSn']
    data = f'seriesSn={seriesSn}&seriesFlag=Y'
    pro_url = f'https://www.autonicschina.cn/series/{seriesSn}'
    resp = requests.post(url='https://www.autonicschina.cn/series/data/init',headers=headers,data=data)
    resultVo = resp.json().get('resultVo')
    mainSfe = resultVo['mainSfe']
    Feature = {}
    advantage = []
    function = {}
    parameter = []
    if mainSfe:
        tree = etree.HTML(mainSfe)
        li_list = tree.xpath('.//ul[@class="dot-list"]/li')
        for li in li_list:
            try:
                advantage.append(li.xpath('.//text()')[0])
            except:
                logger.info(f'no text URL: {pro_url}')
                pass
        # 解析Feature文本和图片
        detail_sec_tree = tree.xpath('.//div[@class="detail-sec"]')
        if detail_sec_tree != []:
            for detail_sec in detail_sec_tree:
                direct_h3_tree = detail_sec.xpath('./h3')
                direct_p_tree = detail_sec.xpath('./p[@class="desc"]')
                direct_ul1_tree = detail_sec.xpath('./ul[@class="list-col col1"]')
                direct_ul2_tree = detail_sec.xpath('./ul[@class="list-col col2"]')
                direct_ul3_tree = detail_sec.xpath('./ul[@class="list-col col3"]')
                if len(direct_h3_tree) == 1 and len(direct_p_tree) == 1 and len(direct_ul1_tree) == 1:
                    h3_text = direct_h3_tree[0].xpath('./text()')[0].strip()
                    p_text = direct_p_tree[0].xpath('./text()')[0].strip()
                    img_list = []
                    img_tree = direct_ul1_tree[0].xpath('.//img')
                    for img in img_tree:
                        img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
                    function[h3_text] = [{'content':p_text,'type':'text'},{'content':img_list,'type':'img'}]
                elif len(direct_h3_tree) == 1 and len(direct_p_tree) == 1 and len(direct_ul2_tree) == 1:
                    h3_text = direct_h3_tree[0].xpath('./text()')[0].strip()
                    p_text = direct_p_tree[0].xpath('./text()')[0].strip()
                    img_list = []
                    img_tree = direct_ul2_tree[0].xpath('.//img')
                    for img in img_tree:
                        img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
                    function[h3_text] = [{'content':p_text,'type':'text'},{'content':img_list,'type':'img'}]
                elif direct_ul2_tree != [] and len(direct_h3_tree) == 0 and len(direct_p_tree) == 0:
                    try:
                        li_list = []
                        for ul2 in direct_ul2_tree:
                            li_list += ul2.xpath('./li')
                        for li in li_list:
                            h3_text_tree = li.xpath('./h3/text()')
                            if h3_text_tree != []:
                                h3_text = h3_text_tree[0].strip()
                            elif li.xpath('./h4/text()') != []:
                                h3_text = li.xpath('./h4/text()')[0].strip()
                            else:
                                h3_text = '体积小重量轻'
                            p_text_tree = li.xpath('./p/text()')
                            img_list = []
                            img_tree = li.xpath('.//img')
                            for img in img_tree:
                                img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
                            if p_text_tree != []:
                                p_text = p_text_tree[0].strip()
                                function[h3_text] = [{'content':p_text,'type':'text'},{'content':img_list,'type':'img'}]
                            else:
                                function[h3_text] = [{'content':img_list,'type':'img'}]
                    except Exception as e:
                        logger.error(f'{e} {pro_url} ul2 1 xpath wrong')
                if direct_ul2_tree != [] and len(direct_h3_tree) == 1 and len(direct_p_tree) == 0:
                    h3_text = direct_h3_tree[0].xpath('./text()')[0].strip()
                    try:
                        img_list = []
                        img_tree = direct_ul2_tree[0].xpath('.//img')
                        for img in img_tree:
                            img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
                        function[h3_text] = [{'content':img_list,'type':'img'}]
                    except Exception as e:
                        logger.error(f'{e} {pro_url} ul2 2 xpath wrong')
                if direct_ul3_tree != []:
                    li_list = []
                    for ul3 in direct_ul3_tree:
                        li_list += ul3.xpath('./li')
                    for li in li_list:
                        try:
                            h4_text_tree = li.xpath('./p[@class="h4"]/text()')
                            p_text_tree = li.xpath('./p[@class="desc"]/text()')
                            img_list = []
                            img_tree = li.xpath('.//img')
                            for img in img_tree:
                                img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
                            if h4_text_tree != [] and p_text_tree != []:
                                h4_text,p_text = h4_text_tree[0].strip(),p_text_tree[0].strip()
                                function[h4_text] = [{'content':p_text,'type':'text'},{'content':img_list,'type':'img'}]
                            elif h4_text_tree == [] and p_text_tree != []:
                                p_text = p_text_tree[0].strip()
                                function[p_text] = [{'content':img_list,'type':'img'}]
                        except Exception as e:
                            logger.error(f'{e} {pro_url} ul3 xpath wrong')
        table_tree = tree.xpath('.//table')
        for table in table_tree:
            table_str = etree.tostring(table, encoding='utf8', method='html').decode()
            parameter.append({'content':table_str,'type':'table'})
    Feature['产品优势'] = advantage
    Feature['主要功能'] = function

    pro_dic = {}
    pro_dic['ProductName'] = resultVo['seriesNm'] + resultVo['skllNm']
    pro_dic['ProductImage'] = 'https://www.autonicschina.cn/web' + resultVo['imageAtchList'][0]['physiclFlpth']
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = mainSfe
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = resultVo['seriesDc']
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = parameter
    final_dic['pro'].append(pro_dic)
    logger.info(f'已爬取{len(final_dic["pro"])}/290条数据,')
    return 

def AUTONICS(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://www.autonicschina.cn/product/class/2000001'
    resp = requests.get(url=origion_url,headers=headers)
    tree = etree.HTML(resp.text)
    series_urls,pro_urls,datas = [],[],[]
    a_list = tree.xpath('//*[@id="lnb"]/div/ul/li[1]/div/div/ul/li/a')
    for a in a_list:
        series_urls.append(urljoin(origion_url,a.xpath('./@href')[0]))
    for series in series_urls:
        headers['Content-Type'] = 'application/json'
        if series == 'https://www.autonicschina.cn/menu/forward/1000006':
            firstTypeName,secondTypeName = '软件',''
            data = json.dumps({"prductCtgrySn":'2000229'})
            resp = requests.post(url='https://www.autonicschina.cn/product/category/series/listData',headers=headers,data=data)
            resultList = resp.json()['resultList']
            for product in resultList:
                seriesSn = product['seriesSn']
                data = f'seriesSn={seriesSn}&seriesFlag=Y'
                pro_url = f'https://www.autonicschina.cn/series/{seriesSn}'
                headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            continue
        resp = requests.get(url=series,headers=headers)
        tree = etree.HTML(resp.text)
        firstTypeName = tree.xpath('//*[@id="content"]/div/div/h2/text()')[0].strip()
        a_list = tree.xpath('.//ul[@class="list-wrap in-image line-type pro-list"]/li/a')
        for a in a_list:
            headers['Content-Type'] = 'application/json'
            prductCtgrySn = a.xpath('./@href')[0].split('/')[-1]
            resp = requests.get(url=f'https://www.autonicschina.cn/product/category/{prductCtgrySn}',headers=headers)
            tree = etree.HTML(resp.text)
            secondTypeName = tree.xpath('//*[@id="content"]/div/div/h2/text()')[0].strip()
            data = json.dumps({"prductCtgrySn":prductCtgrySn})
            resp = requests.post(url='https://www.autonicschina.cn/product/category/series/listData',headers=headers,data=data)
            resultList = resp.json()['resultList']
            with ThreadPoolExecutor(max_workers=20) as executor:
                for i in range(len(resultList)):
                    product = resultList[i]
                    executor.submit(parse_page,product,final_dic,headers,firstTypeName,secondTypeName)
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Content-Type':'application/json',
        'Cookie':'SCOUTER=xtbcrb1og1s9p; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN; Hm_lvt_c17bcc635ddf4acbcce5d710845eea2d=1696669166; _gid=GA1.2.252875720.1696669166; JSESSIONID=B2E3C201DF349BF48369925C492E5F14.tomcat1A; recentPrduct=3000981%2C3000432%2C3000434%2C3000988%2C3000992%2C3000662; Hm_lpvt_c17bcc635ddf4acbcce5d710845eea2d=1696746296; _ga_4L3G8W1216=GS1.1.1696744812.3.1.1696746295.0.0.0; _ga=GA1.2.834675334.1696669166; _gat_gtag_UA_116275600_3=1',
        'Referer':'https://www.autonicschina.cn/series/3000981'
    }
    final_dic = AUTONICS(headers=headers)
    filename=f'奥托尼克斯产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    