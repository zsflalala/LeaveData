import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def parse_propage(pro_url):
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//ol[@class="prodInfo-title"]/text()')[0].strip()
    pro_img = urljoin(pro_url,tree.xpath('.//div[@class="big-img"]/img/@src')[0])
    try:
        firstTypeName = tree.xpath('.//aside[@class="Rightbar"]/div/em/a[4]/text()')[0].strip()
    except:
        firstTypeName = tree.xpath('.//aside[@class="Rightbar"]/div/em/span/text()')[0].strip()
    secondTypeName = tree.xpath('.//aside[@class="Rightbar"]/div/b/text()')[0].strip()
    Description,Parameter = {},[]
    li_list = tree.xpath('.//div[@class="tab"]/ul/li')
    div_list = tree.xpath('.//div[@class="tabinfo"]/div')
    assert len(li_list) == len(div_list)
    for i in range(len(li_list)):
        li,div = li_list[i],div_list[i]
        tab_name = li.xpath('./span/text()')[0]
        tab_img = []
        img_tree = div.xpath('.//img')
        for img in img_tree:
            tab_img.append(urljoin(pro_url,img.xpath('./@src')[0]))
        table_ = []
        if tab_img == []:
            table_tree = div.xpath('.//table')
            for table in table_tree:
                table_str = etree.tostring(table,encoding='utf-8',method='html').decode()
                table_.append({'content':table_str,'type':'table'})
            tab_text = div.xpath('.//text()')
            tab_text = ''.join([item.strip() for item in tab_text])
        if tab_name == '技术参数':
            if tab_img != []:
                Parameter = tab_img
            else:
                Parameter = table_
            continue
        if tab_img != []:
            Description[tab_name] = tab_img
        elif tab_text != '':
            Description[tab_name] = tab_text
        elif table_tree != []:
            Description[tab_name] = table_
        else:
            Description[tab_name] = []
    
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

def GSK(headers):
    final_dic = {'pro':[]}
    series_urls = [f'http://www.gsk.com.cn/cplb/list_27.aspx?lcid=6&page={i}' for i in range(1,6)] + \
                    [f'http://www.gsk.com.cn/cplb/list_27.aspx?lcid=63&page={i}' for i in range(1,5)] + \
                    [f'http://www.gsk.com.cn/cplb/list_27.aspx?lcid=5&page={i}' for i in range(1,7)] + \
                    ['http://www.gsk.com.cn/cplb/list_27.aspx?lcid=146','http://www.gsk.com.cn/cplb/list_27.aspx?lcid=4'] + \
                    [f'http://www.gsk.com.cn/cplb/list_27.aspx?lcid=54&page={i}' for i in range(1,5)] + \
                    [f'http://www.gsk.com.cn/cplb/list_27.aspx?lcid=172&page={i}' for i in range(1,4)]
    for series in series_urls:
        resp = requests.get(url=series,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        a_list = tree.xpath('.//div[@class="prod-list"]/div/a')
        with ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for a in a_list:
                pro_url = urljoin(series_urls[0],a.xpath('./@href')[0])
                logger.info(f'prourl: {pro_url}')
                future = executor.submit(parse_propage,pro_url)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                pro_dic = future.result()
                final_dic['pro'].append(pro_dic)
                logger.info(f'已爬取{len(final_dic["pro"])}/167条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = GSK(headers=headers)
    filename=f'GSK广州数控产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    