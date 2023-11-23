import re
import sys
import json
import requests
from lxml import etree
from urllib.parse import urljoin
import os
import argparse
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# 1636

def parse_args():
    parser = argparse.ArgumentParser(description='部件库-B2B商城-国际-evcc.com')
    parser.add_argument('-w', '--maxworker', default=10, type=int, help='threed pool max_worker')
    parser.add_argument('-s', '--startpage', default=1, type=int, help='spider start page')
    parser.add_argument('-e', '--endpage', default=76, type=int, help='spider end page')
    args = parser.parse_args()
    return args


def get_pro_url(url,headers,pro_urls):
    proxies = {
        'http':'http://113.124.87.144:9999'
    }
    try:
        resp = requests.get(url=url,headers=headers,timeout=(1,20))
        tree = etree.HTML(resp.text)
        div_list = tree.xpath('.//div[@class="list-items"]/div[@class="list-item"]')
        for div in div_list:
            pro_url = div.xpath('./div/div//a/@href')[0]
            pro_urls.append(urljoin(url,pro_url))
    except Exception as e:
        logger.error(f'{e} URL: {url}')
    return None

def parse_page(url,headers):
    pro_dic = {}
    pro_dic['first_type'] = 'Motor'
    pro_dic['second_type'] = 'DC_Motor'
    pro_dic['url'] = url
    try:
        resp = requests.get(url=url,headers=headers,timeout=(1,20))
    except:
        logger.error(f'ParsePage Request Time Out. URL: {url}')
        return pro_dic
    tree = etree.HTML(resp.text)
    pro_dic['html'] = resp.text
    pro_img = []
    ProductDetails,ProductParameters,Specifications = {},{},{}
    PDcols_warp_tree = tree.xpath('.//div[@class="PDcols-warp"]/div//h1')
    # 表格类页面
    if PDcols_warp_tree == []:
        pro_name = tree.xpath('.//h1[@class="details-content-spc-title spc-width-active"]/text()')[0].strip()
        pro_img_tree = tree.xpath('.//ul[@id="uProductImgs"]')
        img_list = pro_img_tree[0].xpath('.//img')
        for img in img_list:
            pro_img.append(urljoin(url,img.xpath('./@src')[0]))
        detail_tree = tree.xpath('.//div[@class="details-content-parameter"]')
        assert len(detail_tree) == 2
        
        th_list,td_list = [],[]
        table_th_tree = detail_tree[0].xpath('.//table//th')
        table_td_tree = detail_tree[0].xpath('.//table//td')
        for th in table_th_tree:
            th_list.append(''.join([item.strip() for item in th.xpath('.//text()')]))
        for td in table_td_tree:
            td_list.append(''.join([item.strip() for item in td.xpath('.//text()')]))
        
        assert len(th_list) == len(td_list)
        for i in range(len(th_list)):
            ProductDetails[th_list[i]] = td_list[i]

        # 部分界面有文字和图片
        text = tree.xpath('.//div[@class="details-content-parameter"]//p//text()')
        text = ''.join([item.strip() for item in text]).replace('More Parameter >','')
        ProductDetails['MoreParameter'] = text
        ProductDetails['img'] = []
        img_tree = tree.xpath('.//div[@class="details-content-describe"]//img')
        if img_tree != []:
            for img in img_tree:
                ProductDetails['img'].append(urljoin(url,img.xpath('./@src')[0]))
        
        th_list,td_list = [],[]
        table_th_tree = detail_tree[1].xpath('.//table//th')
        table_td_tree = detail_tree[1].xpath('.//table//td')
        for th in table_th_tree:
            th_list.append(''.join([item.strip() for item in th.xpath('.//text()')]))
        for td in table_td_tree:
            td_list.append(''.join([item.strip() for item in td.xpath('.//text()')]))
        
        assert len(th_list) == len(td_list)
        for i in range(len(th_list)):
            ProductParameters[th_list[i]] = td_list[i]
    else:
        pro_name = PDcols_warp_tree[0].xpath('./text()')[0].strip()
        pro_img_tree = tree.xpath('.//div[@class="thumbnail"]')
        img_list = pro_img_tree[0].xpath('.//img')
        for img in img_list:
            pro_img.append(urljoin(url,img.xpath('./@src')[0]))

        packdiv_tree = tree.xpath('.//div[@class="packdiv"]')
        if packdiv_tree != []:
            th_list,td_list = [],[]
            table_th_tree = packdiv_tree[0].xpath('.//table//th')
            table_td_tree = packdiv_tree[0].xpath('.//table//td')
            for th in table_th_tree:
                th_list.append(''.join([item.strip() for item in th.xpath('.//text()')]))
            for td in table_td_tree:
                td_list.append(''.join([item.strip() for item in td.xpath('.//text()')]))
            assert len(th_list) == len(td_list)
            for i in range(len(th_list)):
                ProductDetails[th_list[i]] = td_list[i]
        ProductDetails['MoreParameter'] = ''
        ProductDetails['img'] = []

        li_tree = tree.xpath('.//ul[@class="attr-list"]/li')
        if li_tree != []:
            for li in li_tree:
                attr_name = li.xpath('./span[1]/text()')[0].strip()
                attr_value = li.xpath('./span[2]/text()')[0].strip()
                ProductParameters[attr_name] = attr_value

        specifications_tree = tree.xpath('.//div[@class="specifications"]')
        if specifications_tree != []:
            text = specifications_tree[0].xpath('.//text()')
            text = ''.join([item.strip() for item in text]).replace('Specifications','')
            Specifications['text'] = text
            
            img_list = []
            img_tree = specifications_tree[0].xpath('.//img')
            if img_tree != []:
                for img in img_tree:
                    img_list.append(urljoin(url,img.xpath('./@src')[0]))
            Specifications['img'] = img_list

    pro_dic['ProductName'] = pro_name
    pro_dic['ProductImg'] = pro_img
    pro_dic['ProductDetails'] = ProductDetails
    pro_dic['ProductParameters'] = ProductParameters
    pro_dic['Specifications'] = Specifications
    
    return pro_dic,url


@logger.catch
def evcc_main(args):
    final_dic = {'pro':[]}
    pro_urls = []
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    with ThreadPoolExecutor(max_workers=args.maxworker) as executor:
        for i in range(args.startpage,args.endpage):
            url = f'https://www.ecvv.com/catalog/dc-motor_cid100007153.html?pageindex={i}' # 1 - 76
            url = f'https://www.ecvv.com/catalog/ac-motor_cid100007154.html?pageindex={i}' # 1 - 113
            url = f'https://www.ecvv.com/catalog/stepper-motor_cid100007155.html?pageindex={i}' # 1 - 128
            executor.submit(get_pro_url,url,headers,pro_urls)
    pro_urls = list(set(pro_urls))
    with ThreadPoolExecutor(max_workers=args.maxworker) as executor:
        to_do = []
        for url in pro_urls:
            try:
                future = executor.submit(parse_page,url,headers)
                to_do.append(future)
            except:
                logger.error(f'解析页面失败，页面: {pro_urls.index(url) // 30 + 1}，链接: {url}')
        for future in concurrent.futures.as_completed(to_do):
            pro_dic,url = future.result()
            final_dic['pro'].append(pro_dic)
            logger.info(f'已完成第{pro_urls.index(url)+1:>4}/{len(pro_urls)}产品爬取')
    
    filename,dic = 'temp.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取完成，存储在{filename}中.')
    return None


if __name__ =='__main__':
    args = parse_args()
    logger.add(sys.stderr,format="{time} {level} {message}",filter="my_module", level="INFO")
    logger.add("runtime.log",retention="1 day")
    evcc_main(args)
