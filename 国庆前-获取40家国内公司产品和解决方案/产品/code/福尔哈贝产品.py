import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def get_prourl(series_url,headers):
    ProductUrl = []
    resp = requests.get(url=series_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    try:
        secondTypeName = tree.xpath('.//h1[@class="headline headline--h2 headline--semiBold headline--left"]//text()')
        secondTypeName = ''.join([item.strip() for item in secondTypeName]).replace('\xa0','')
    except:
        try:
            secondTypeName = tree.xpath('.//h1[@class="headline headline--h2 headline--semiBold headline--left"]//text()')
            secondTypeName = ''.join([item.strip() for item in secondTypeName]).replace('\xa0','')
        except:
            secondTypeName = ''
    div_list = tree.xpath('.//div[@class="teaserbox__elementWrapper swiper-wrapper"]/div')
    for div in div_list:
        kind_url = urljoin(series_url,div.xpath('./a/@href')[0])
        resp = requests.get(url=kind_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="search__resultList resultList--product results-list"]/li')
        for li in li_list:
            ProductUrl.append(urljoin(series_url,li.xpath('./div/div[1]//a/@href')[0]))
    if ProductUrl == []:
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="search__resultList resultList--product results-list"]/li')
        for li in li_list:
            ProductUrl.append(urljoin(series_url,li.xpath('.//div[@class="product__summary"]/a/@href')[0]))
    return secondTypeName,ProductUrl

@logger.catch
def parse_propage(pro_url,firstTypeName,secondTypeName):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//h1[@class="headline--h2 headline--blue"]/span[1]/text()')[0]
    pro_name += tree.xpath('//*[@id="lower"]/div[2]/div[2]/div[2]/div[2]/div[1]/text()')[0].strip()
    pro_name = ''.join([item.strip() for item in pro_name])
    pro_img = []
    img_list = tree.xpath('.//div[@class="swiper-wrapper productGallery__thumbs"]//img')
    for img in img_list:
        pro_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    Description = []
    descrip = tree.xpath('.//h2[@class="productAttributes__dataHeadline headline--h3"]//text()')
    descrip = ''.join([item.strip() for item in descrip])
    Description.append(descrip)
    descrip2 = tree.xpath('.//div[@class="productAttributes__dataKey"]')
    if descrip2 != []:
        try:
            descrip2 = descrip2[0].xpath('./text()')[0].strip() + '--'
            div_list = tree.xpath('.//div[@class="productAttributes__dataTable"]/div')
            for i in range(len(div_list)):
                div = div_list[i]
                text = div.xpath('./text()')[0].strip()
                if i % 2 == 0:
                    text = text + ';'
                descrip2 += text
        except:
            descrip2 = tree.xpath('.//div[@class="productAttributes__dataTable"]//text()')
            descrip2 = ''.join([item.strip() for item in descrip2])
        Description.append(descrip2)
    Feature = []
    div_list = tree.xpath('.//div[@class="productDetail__advantagesItemText"]/text()')
    for div in div_list:
        Feature.append(div.strip())
    Parameter = {}

    values = []
    values_table = tree.xpath('.//div[@id="tab-values"]//table')
    for value in values_table:
        value_str = etree.tostring(value,encoding='utf-8',method='html').decode()
        values.append({'content':value_str,'type':'table'})
    Parameter['值'] = values

    rangechart_tree = tree.xpath('.//div[@id="tab-range-chart"]')[0]
    text = rangechart_tree.xpath('.//text()')
    text = ''.join([item.strip() for item in text])
    img_list = []
    img_tree = rangechart_tree.xpath('.//img')
    for img in img_tree:
        img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
    text_dic = {'content':text,'type':'text'}
    img_dic = {'content':img_list,'type':'img'}
    Parameter['特征曲线'] = [text_dic,img_dic]

    drawingsTab_tree = tree.xpath('.//div[@id="tab-range-chart"]')
    img_list = []
    img_tree = drawingsTab_tree[0].xpath('.//img')
    for img in img_tree:
        img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
    download_tree = drawingsTab_tree[0].xpath('.//a')
    for download in download_tree:
        img_list.append(urljoin(pro_url,download.xpath('./@href')[0]))
    Parameter['尺寸图'] = img_list

    options_tree = tree.xpath('.//div[@id="tab-options"]')
    img_list = []
    img_tree = options_tree[0].xpath('.//img')
    for img in img_tree:
        img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
    Parameter['选配件'] = img_list

    combinations_tree = tree.xpath('.//div[@id="tab-combinations"]')
    img_list = []
    img_tree = combinations_tree[0].xpath('.//a[@class="combinations__productSeriesLinksDatasheet dataSheetLink"]')
    for img in img_tree:
        img_list.append(urljoin(pro_url,img.xpath('./@href')[0]))
    Parameter['产品组合'] = img_list

    downloads_tree = tree.xpath('.//div[@id="tab-downloads"]')
    img_list = []
    img_tree = downloads_tree[0].xpath('.//a')
    for img in img_tree:
        img_list.append(urljoin(pro_url,img.xpath('./@href')[0]))
    Parameter['下载'] = img_list

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
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def FAULHABER(headers):
    final_dic = {'pro':[]}
    origion_url = 'https://faulhaber.com.cn/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    a_list = tree.xpath('.//div[@id="65218"]//div[@class="swiper-slide"]//a')
    for a in a_list:
        series_url = urljoin(origion_url,a.xpath('./@href')[0])
        resp = requests.get(url=series_url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        try:
            firstTypeName = tree.xpath('.//div[@class="submenu__startItem js-submenu-startItem"]/a/text()')[0].strip()
            series_urls = tree.xpath('.//div[@class="scrollableHeader__innerScrollList"]/a/@href')
            for series_url in series_urls:
                secondTypeName,pro_urls = get_prourl(series_url,headers)
                logger.info(f'{firstTypeName},{secondTypeName},{len(pro_urls)}')
                with ThreadPoolExecutor(max_workers=10) as executor:
                    to_do = []
                    for pro_url in pro_urls:
                        to_do.append(executor.submit(parse_propage,pro_url,firstTypeName,secondTypeName))
                    for future in concurrent.futures.as_completed(to_do):
                        pro_dic = future.result()
                        final_dic['pro'].append(pro_dic)
                        logger.info(f'已爬取{len(final_dic["pro"])}/245条数据')
        except:
            firstTypeName_tree = tree.xpath('.//p[@class="headline headline--h1 headline--left"]/text()')
            if firstTypeName_tree != []:
                firstTypeName = firstTypeName_tree[0].strip()
            else:
                firstTypeName = tree.xpath('.//h1[@class="headline headline--h1 headline--left"]/text()')[0].strip()
            secondTypeName,pro_urls = get_prourl(series_url,headers)
            logger.info(f'{firstTypeName},{secondTypeName},{len(pro_urls)}')
            with ThreadPoolExecutor(max_workers=10) as executor:
                to_do = []
                for pro_url in pro_urls:
                    to_do.append(executor.submit(parse_propage,pro_url,firstTypeName,secondTypeName))
                for future in concurrent.futures.as_completed(to_do):
                    pro_dic = future.result()
                    final_dic['pro'].append(pro_dic)
                    logger.info(f'已爬取{len(final_dic["pro"])}/245条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = FAULHABER(headers=headers)
    filename=f'福尔哈贝产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    