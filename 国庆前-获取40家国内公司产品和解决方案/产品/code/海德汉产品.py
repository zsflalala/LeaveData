import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
from html import unescape
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def parse_propage(pro_url,firstTypeName='',secondTypeName=''):
    isError = 0
    pro_name,pro_img = '',[]
    Description,Feature,Parameter = [],[],[]
    resp = requests.get(url=pro_url,headers=headers,timeout=(2,10))
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    pro_name = tree.xpath('.//title/text()')[0].strip()
    img_tree = tree.xpath('.//div[@class="page-content"]//img')
    for img in img_tree:
        pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    firstTypeName = tree.xpath('//div[@itemprop="itemListElement"]/a/span/text()')[2].strip()
    # Description
    desp_text = tree.xpath('.//div[@class="textpart1 fl" or @class="page-content"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    for table in tree.xpath('.//div[@class="site-container"]//table'):
        table_text = table.xpath('.//text()')
        table_text = ''.join([item.strip() for item in table_text])
        desp_text = desp_text.replace(table_text,'')
        table_str = etree.tostring(table,encoding='utf-8').decode()
        Description.append({'content':table_str,'type':'table'})
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})

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
    if not bool(Description) and not bool(Feature):
        isError = 1
    return pro_dic,isError

def HOLLYSYS(headers):
    final_dic = {'pro':[]}
    urls = [
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E5%B0%81%E9%97%AD%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lic/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lip/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lif/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/lida-473483/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/lida-475485/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/lida-477487/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/lida-479489/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/lida-277287/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-lida/lida-279289/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-pp/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-for-pp/pp-281-r/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-lipliflic-vacuum/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E9%95%BF%E5%BA%A6%E6%B5%8B%E9%87%8F/%E6%95%9E%E5%BC%80%E5%BC%8F%E5%85%89%E6%A0%85%E5%B0%BA/selection-guide-lipliflic-vacuum/lip-481v-lip-481u/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/%E5%B0%81%E9%97%AD%E5%BC%8F%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/%E5%85%89%E5%AD%A6%E6%89%AB%E6%8F%8F%E7%9A%84%E6%A8%A1%E5%9D%97%E5%9E%8B%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/%E7%A3%81%E6%80%A7%E6%89%AB%E6%8F%8F%E7%9A%84%E6%A8%A1%E5%9D%97%E5%9E%8B%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8/%E8%A7%92%E5%BA%A6%E7%BC%96%E7%A0%81%E5%99%A8%E6%A8%A1%E5%9D%97/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E6%97%8B%E8%BD%AC%E7%BC%96%E7%A0%81%E5%99%A8/%E5%B8%A6%E5%86%85%E7%BD%AE%E8%BD%B4%E6%89%BF/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E6%97%8B%E8%BD%AC%E7%BC%96%E7%A0%81%E5%99%A8/%E6%97%A0%E5%86%85%E7%BD%AE%E8%BD%B4%E6%89%BF/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/tnc-640/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/tnc-620/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/tnc-320/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/tnc-128/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/cnc-pilot-640/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/manualplus-620/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/connected-machining/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/connected-machining/heidenhain-dnc/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/connected-machining/statemonitor/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/connected-machining/extended-workspace/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/cnc%E6%8E%A7%E5%88%B6%E5%99%A8/connected-machining/remote-desktop-manager/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E5%90%8E%E7%BB%AD%E7%94%B5%E8%B7%AF/%E8%AF%84%E4%BC%B0%E7%94%B5%E8%B7%AF/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E5%90%8E%E7%BB%AD%E7%94%B5%E8%B7%AF/%E6%95%B0%E6%98%BE%E8%A3%85%E7%BD%AE/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E5%90%8E%E7%BB%AD%E7%94%B5%E8%B7%AF/%E6%8E%A5%E5%8F%A3%E7%94%B5%E5%AD%90%E7%94%B5%E8%B7%AF/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E5%90%8E%E7%BB%AD%E7%94%B5%E8%B7%AF/%E6%B5%8B%E9%87%8F%E5%92%8C%E6%A3%80%E6%B5%8B%E8%AE%BE%E5%A4%87/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E6%B5%8B%E5%A4%B4/',
        'https://www.heidenhain.com.cn/zh_CN/%E4%BA%A7%E5%93%81%E4%B8%8E%E5%BA%94%E7%94%A8/%E6%AF%94%E8%BE%83%E7%B3%BB%E7%BB%9F/kgm/'
    ]
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
    }
    final_dic = HOLLYSYS(headers=headers)
    filename=f'海德汉产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    