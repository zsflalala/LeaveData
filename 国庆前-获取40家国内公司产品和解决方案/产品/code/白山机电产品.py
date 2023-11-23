import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


@logger.catch
def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('.//ul[@class="basic_crumbs_list scrollbar"]/li')
    pro_name = li_list[-1].xpath('./a/text()')[0].strip()
    pro_img = urljoin(pro_url,tree.xpath('.//div[@class="detail_big_pic_content"]/img/@src')[0])
    firstTypeName =  li_list[-2].xpath('./a/text()')[0].strip()
    secondTypeName =  li_list[-3].xpath('./a/text()')[0].strip()

    Description,Parameter = {},{}
    Description['基本概述'] = []
    simple_text = tree.xpath('.//div[@class="detail_content"]//text()')
    simple_text = ''.join([item.strip() for item in simple_text])
    if simple_text != '':
        Description['基本概述'].append({'content':simple_text,'type':'text'})
    tab_name = tree.xpath('.//div[@class="product_specific_content"]')[1].xpath('./div[1]//text()')
    tab_content = tree.xpath('.//div[@class="product_specific_content"]')[1].xpath('./div[2]/div')
    assert len(tab_name) == len(tab_content)
    for i in range(len(tab_content)):
        name,content = tab_name[i],tab_content[i]
        if i == 0:
            Description[name] = []
            all_text = content.xpath('.//text()')
            all_text = ' '.join([item.strip() for item in all_text])
            img_list = []
            img_tree = content.xpath('.//img')
            for img in img_tree:
                img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
            table_list = []
            table_tree = content.xpath('.//table')
            for table in table_tree:
                table_list.append(etree.tostring(table,encoding='utf-8').decode())
                table_text = table.xpath('.//text()')
                table_text = ' '.join([item.strip() for item in table_text])
                all_text = all_text.replace(table_text,'')
            if all_text != '':
                Description[name].append({'content':all_text,'type':'text'})
            if img_list != []:
                Description[name].append({'content':img_list,'type':'img'})
            if table_list != []:
                Description[name].append({'content':table_list,'type':'table'})
        else:
            Parameter[name] = []
            img_list = []
            img_tree = content.xpath('.//img')
            for img in img_tree:
                img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
            table_list = []
            table_tree = content.xpath('.//table')
            for table in table_tree:
                table_list.append(etree.tostring(table,encoding='utf-8').decode())
            down_tree = content.xpath('.//a')
            for a in down_tree:
                img_list.append(urljoin(pro_url,a.xpath('./@href')[0]))
            if img_list != []:
                Parameter[name].append({'content':img_list,'type':'img'})
            if table_list != []:
                Parameter[name].append({'content':table_list,'type':'table'})
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

def BAISHAN(headers):
    final_dic = {'pro':[]}
    series_urls = []
    origion_url = 'https://www.bsjd.com/product-200010.html'
    resp = requests.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    li_list = tree.xpath('.//li[@class="leve_1_content"]')
    del li_list[0]
    for li in li_list:
        series_urls.append(urljoin(origion_url,li.xpath('./div[1]//a/@href')[0]))
    for series in series_urls:
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//div[@class="product_list_0"]/div/a')
        if series == 'https://www.bsjd.com/product-200011.html':
            for i in range(2,7):
                url = f'https://www.bsjd.com/product-200011.html#cache_list_page_858205={i}'
                resp = requests.get(url=url,headers=headers)
                resp.encoding = 'utf-8'
                tree = etree.HTML(resp.text)
                a_list += tree.xpath('.//div[@class="product_list_0"]/div/a')
        elif series == 'https://www.bsjd.com/product-200012.html':
            for i in range(2,4):
                url = f'https://www.bsjd.com/product-200012.html#cache_list_page_858205={i}'
                resp = requests.get(url=url,headers=headers)
                resp.encoding = 'utf-8'
                tree = etree.HTML(resp.text)
                a_list += tree.xpath('.//div[@class="product_list_0"]/div/a')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for a in a_list:
                pro_url = urljoin(series_urls[0],a.xpath('./@href')[0])
                future = executor.submit(parse_propage,pro_url)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/64条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = BAISHAN(headers=headers)
    filename=f'白山机电产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    