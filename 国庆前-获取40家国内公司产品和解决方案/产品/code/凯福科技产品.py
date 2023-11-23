import json
import requests
from lxml import etree
from loguru import logger


def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@class="product-des"]/h2/text()')[0]
    pro_img = []
    img_list = tree.xpath('.//ul[@id="thumblist"]//img')
    for img in img_list:
        pro_img.append(img.xpath('./@src')[0])
    firstTypeName = tree.xpath('.//div[@class="cate-position cate-position-detail"]/div/a[2]/text()')[0]
    secondTypeName = tree.xpath('.//div[@class="cate-position cate-position-detail"]/div/a[3]/text()')[0]
    Description = []
    des_text = tree.xpath('.//div[@class="p-desc"]/p/text()')
    for text in des_text:
        text = text.strip().replace(' ','').replace('\xa0','')
        if text:
            Description.append(text)
    Parameter = []
    parameter_img_list = []
    parameter_img_tree = tree.xpath('.//div[@class="product-detail-body bg-fff"]//div[@class="bd"]/div[1]//img')
    for img in parameter_img_tree:
        parameter_img_list.append(img.xpath('./@src')[0])
    Parameter.append({'技术参数':parameter_img_list})
    table_tree = tree.xpath('.//div[@class="product-detail-body bg-fff"]//div[@class="bd"]/div[1]//table')
    for table in table_tree:
        table_str = etree.tostring(table, encoding='utf8', method='html').decode()
        Parameter.append({'技术参数':table_str,'type':'table'})
    size_img_list = []
    size_img_tree = tree.xpath('.//div[@class="product-detail-body bg-fff"]//div[@class="bd"]/div[2]//img')
    for img in size_img_tree:
        size_img_list.append(img.xpath('./@src')[0])
    Parameter.append({'产品尺寸':size_img_list})
    use_img_list = []
    use_img_tree = tree.xpath('.//div[@class="product-detail-body bg-fff"]//div[@class="bd"]/div[3]//img')
    for img in use_img_tree:
        use_img_list.append(img.xpath('./@src')[0])
    Parameter.append({'使用说明':use_img_list})
    pro_dic = {}
    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImage'] = pro_img
    pro_dic['ProductUrl'] = pro_url
    pro_dic['ProductHTML'] = resp.text.strip()
    pro_dic['ProductJSON'] = ''
    pro_dic['FirstType'] = firstTypeName
    pro_dic['SecondType'] = secondTypeName
    pro_dic['ProductDetail'] = {}
    pro_dic['ProductDetail']['Description'] = Description
    pro_dic['ProductDetail']['Feature'] = []
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def KAIFULL(headers):
    final_dic = {'pro':[]}
    series_urls = []
    origion_url = 'http://www.kaifull.net/product/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//li[@class="pro-li "]//div[@class="left"]//a')
    for a in a_list:
        series_urls.append(a.xpath('./@href')[0])
    del series_urls[-1],series_urls[-1],series_urls[-1],series_urls[0]
    for series in series_urls:
        kind_urls = []
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//ul[@class="plist-class3"]/li/a')
        for a in a_list:
            kind_urls.append(a.xpath('./@href')[0])
        for kind in kind_urls:
            resp = requests.get(url=kind,headers=headers)
            resp.encoding = 'utf-8'
            tree = etree.HTML(resp.text)
            a_list = tree.xpath('.//ul[@class="plist-list"]/li/div[1]/a')
            for a in a_list:
                pro_url = a.xpath('./@href')[0]
                # logger.info(f'prourl: {pro_url}')
                pro_dic = parse_propage(pro_url)
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/222条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = KAIFULL(headers=headers)
    filename=f'凯福科技产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    