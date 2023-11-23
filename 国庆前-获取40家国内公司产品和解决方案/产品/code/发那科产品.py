import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def parse_serise(series,pro_urls,headers,firstTypeName):
    pro_list = []
    for url in pro_urls:
        temp_dic = {}
        resp = requests.get(url=url,headers=headers)
        tree = etree.HTML(resp.text)
        if series == '新能源汽车电驱系列':
            pro_name = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/div/div/text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            if pro_name == '':
                pro_name = tree.xpath('.//div[@class="ytable-cell left"]/div[@class="tit"]/span/text()')[0]
            pro_desc = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/dd//text()')
            if pro_desc == []:
                pro_desc = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/p//text()')
            pro_desc = ''.join([item.strip() for item in pro_desc])
        else:
            pro_name = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/div//text()')
            pro_name = ''.join([item.strip() for item in pro_name])
            pro_desc = tree.xpath('/html/body/div[2]/div[1]/div/div[1]/dl/p//text()')
            pro_desc = ''.join([item.strip() for item in pro_desc])

        pro_img = urljoin(url,tree.xpath('.//div[@class="pic"]/img/@src')[0]) 
        
        pro_feature = []
        dl_list = tree.xpath('.//div[@class="box_item box2"]/div/dl')
        if pro_feature == [] and pro_name == '主驱电机控制器':
            dl_list = tree.xpath('/html/body/div[2]/div[2]/div[2]/dl/dd')
        for dd in dl_list:
            feature = dd.xpath('.//text()')
            feature = ''.join([item.strip() for item in feature])
            pro_feature.append(feature)
        

        application = []
        li_list = tree.xpath('/html/body/div[2]/div[3]/div/ul/div/div/li')
        for li in li_list:
            application.append(li.xpath('//text()')[0])
            
        
        args = []
        li_list = tree.xpath('.//div[@class="box_item box4"]//li')
        for li in li_list:
            args.append(urljoin(url,li.xpath('.//div[@class="pic"]/img/@src')[0]))
        
        download = {}
        boxitem_box5 = tree.xpath('.//div[@class="box_item box5"]')
        if boxitem_box5 != []:
            ul_list = boxitem_box5[0].xpath('./div/ul')
            for ul in ul_list:
                data_name = ul.xpath('./@data-name')[0]
                download[data_name] = []
                li_list = ul.xpath('./li')
                for li in li_list:
                    download[data_name].append(urljoin(url,li.xpath('./a/@href')[0]))
     
        Parameter = {'产品参数':args,'资料下载':download}
        temp_dic['ProductName'] = pro_name
        temp_dic['ProductImage'] = pro_img
        temp_dic['ProductUrl'] = url
        temp_dic['ProductHTML'] = resp.text
        temp_dic['ProductJSON'] = ''
        temp_dic['FirstType'] = firstTypeName
        temp_dic['SecondType'] = ''
        temp_dic['ProductDetail'] = {}
        temp_dic['ProductDetail']['Description'] = pro_desc
        temp_dic['ProductDetail']['Feature'] = pro_feature
        temp_dic['ProductDetail']['Parameter'] = Parameter
        pro_list.append(temp_dic)
    return pro_list

def FANUC(headers):
    final_dic = {'pro':[]}
    urls = [
        'https://www.shanghai-fanuc.com.cn/smallrobots/',
        'https://www.shanghai-fanuc.com.cn/mediumrobots/',
        'https://www.shanghai-fanuc.com.cn/bigrobots/',
        'https://www.shanghai-fanuc.com.cn/scararobots/',
        'https://www.shanghai-fanuc.com.cn/parallelrobots/',
        'https://www.shanghai-fanuc.com.cn/cooperativerobots/',
        'https://www.shanghai-fanuc.com.cn/paintrobots/'
    ]
    for url in urls:
        resp = requests.Session().get(url=url,headers=headers,verify=False)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        div_list = tree.xpath('.//div[@class="exhibition clearfix"]/div')
        for div in div_list:
            pro_dic = {}
            pro_name = div.xpath('.//p[@class="text-title"]/text()')[0]
            pro_img = urljoin(url,div.xpath('.//img/@src')[0])
            firstTypeName = tree.xpath('.//p[@class="wow slideInUp animated navgation"]/span[3]/a/text()')[0]
            ParameterDownload = urljoin(url,div.xpath('./a/@href')[0])
            ParameterText = []
            li_list = div.xpath('.//li')
            for li in li_list:
                text = li.xpath('.//text()')
                text = ''.join([item.strip() for item in text])
                ParameterText.append(text)
            Parameter = {'产品参数':ParameterText,'参数文档':ParameterDownload}
            pro_dic['ProductName'] = pro_name
            pro_dic['ProductImage'] = pro_img
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = firstTypeName
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = ''
            pro_dic['ProductDetail']['Feature'] = []
            pro_dic['ProductDetail']['Parameter'] = Parameter
            final_dic['pro'].append(pro_dic)
            logger.info(f'已爬取{len(final_dic["pro"])}/123条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = FANUC(headers=headers)
    filename=f'发那科产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    