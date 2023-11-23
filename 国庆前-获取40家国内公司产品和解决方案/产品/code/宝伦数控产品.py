import re
import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url,firstTypeName,secondTypeName):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//h1[@class="e_title d_Title p_Title h2"]/div//text()')
    pro_name = ''.join([item.strip() for item in pro_name])
    pro_img = []
    img_dic = json.loads(re.findall("imageJson:'(.*?)',",resp.text)[0])
    for dic in img_dic['navs']:
        pro_img.append(urljoin(pro_url,dic['srcBigPic']))
    Description,Parameter = [],[]
    descpt_text = tree.xpath('.//div[@data-ename="描述内容区"]/div//text()')
    descpt_text = ''.join([item.strip() for item in descpt_text])
    descpt_img = []
    img_tree = tree.xpath('.//div[@data-ename="描述内容区"]/div//img')
    for img in img_tree:
        descpt_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    tables = []
    descpt_table = tree.xpath('.//div[@data-ename="描述内容区"]//table')
    for table in descpt_table:
        tables.append(etree.tostring(table,encoding='utf-8').decode())
    if descpt_text != '':
        Description.append({'content':descpt_text,'type':'text'})
    if descpt_img != []:
        Description.append({'content':descpt_img,'type':'img'})
    if tables != []:
        Description.append({'content':tables,'type':'table'})
    
    parameter_text = tree.xpath('.//div[@class="e_box d_customBoxA hide TabCont"]//text()')
    parameter_text = ''.join([item.strip() for item in parameter_text])
    para_img = []
    img_tree = tree.xpath('.//div[@class="e_box d_customBoxA hide TabCont"]//img')
    for img in img_tree:
        para_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
    tables = []
    para_table = tree.xpath('.//div[@class="e_box d_customBoxA hide TabCont"]//table')
    for table in para_table:
        tables.append(etree.tostring(table,encoding='utf-8').decode())
    if parameter_text != '':
        Parameter.append({'content':parameter_text,'type':'text'})
    if para_img != []:
        Parameter.append({'content':para_img,'type':'img'})
    if tables != []:
        Parameter.append({'content':tables,'type':'table'})

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

def POWERLAND(headers):
    final_dic = {'pro':[]}
    origion_url = 'http://www.power-land.com/product/12/'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('//*[@id="c_portalResnav_main-15916701282697189"]/div/nav/ul/li[3]/ul/li')              
    for li in li_list:
        firstTypeName = li.xpath('./h3/a/text()')[0].strip()
        ul_li_list = li.xpath('./ul/li')
        for li in ul_li_list:
            secondTypeName = li.xpath('./h3/a/text()')[0].strip()
            series_url = urljoin(origion_url,li.xpath('.//a/@href')[0])
            resp = requests.get(url=series_url,headers=headers)
            resp.encoding = 'utf-8'
            tree = etree.HTML(resp.text)
            product_tree = tree.xpath('.//div[@class="proLi"]')
            with ThreadPoolExecutor(max_workers=10) as executor:
                to_do = []
                for product in product_tree:
                    pro_url = urljoin(origion_url,product.xpath('./div/div[2]/a/@href')[0])
                    future = executor.submit(parse_propage,pro_url,firstTypeName,secondTypeName)
                    to_do.append(future)
                for future in concurrent.futures.as_completed(to_do):
                    pro_dic = future.result()
                    final_dic['pro'].append(pro_dic)
                    logger.info(f'已爬取{len(final_dic["pro"])}/43条数据')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        future = executor.submit(parse_propage,'http://www.power-land.com/product/82.html','数字运动控制器','GALIL Ethernet 独立型运动控制器')
        to_do.append(future)
        future = executor.submit(parse_propage,'http://www.power-land.com/product/44.html','数字运动控制器','GALIL Ethernet 独立型运动控制器')
        to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic = future.result()
            final_dic['pro'].append(pro_dic)
            logger.info(f'已爬取{len(final_dic["pro"])}/43条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = POWERLAND(headers=headers)
    filename=f'宝轮数控产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    