import requests
from lxml import etree
import json
from urllib.parse import urljoin


def parse_page(url,headers):
    pro_dic = {}
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    try:
        pro_img = urljoin(url,tree.xpath('.//div[@class="img"]/img/@src')[0]) 
        pro_name = tree.xpath('.//div[@class="show_right fr"]/h2/text()')[0]
        pro_info = tree.xpath('.//div[@class="show_info"]//text()')
        pro_info = ''.join([item.strip() for item in pro_info])

        sample_down = tree.xpath('.//div[@class="show_down clearfix"]/a[1]/@href')[0]
        if sample_down != '':
            sample_down = urljoin(url,sample_down) 
        paper_down = tree.xpath('.//div[@class="show_down clearfix"]/a[2]/@href')[0]
        if paper_down != '':
            paper_down = urljoin(url,sample_down) 
        
        pro_info_imgs = []
        img_list = tree.xpath('.//div[@class="detail show_detail"]//img')
        for img in img_list:
            pro_info_imgs.append(urljoin(url,img.xpath('./@src')[0]))
        pro_dic['产品名称'] = pro_name
        pro_dic['产品图片'] = pro_img
        pro_dic['产品介绍'] = pro_info
        pro_dic['产品详情'] = pro_info_imgs
        pro_dic['样本下载'] = sample_down
        pro_dic['图纸下载'] = paper_down
    except:
        print('出错url: ',url)
    return pro_dic
    

def Damakawa_moter(headers,filename='damakawa.json'):
    kinds = ['电机','减速器','防爆电机']
    final_dic = {'电机':{},'减速器':{},'防爆电机':{}}
    urls = [
        'http://tama-kawa.com/dj/' ,
        'http://tama-kawa.com/jsj/',
        'http://tama-kawa.com/fbdj/'
    ]
    for i in range(3):
        page_urls = []
        url = urls[i]
        resp = requests.get(url=url,headers=headers)
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('.//ul[@class="pro_nul clearfix"]/li')
        for li in li_list:
            page_urls.append(urljoin(url,li.xpath('./a/@href')[0]))
        for page_url in page_urls:
            resp = requests.get(url=page_url,headers=headers)
            tree = etree.HTML(resp.text)
            pro_urls = tree.xpath('.//ul[@class="pro_nul clearfix"]/li')
            for pro_url in pro_urls:
                pro_url = urljoin(url,pro_url.xpath('./a/@href')[0])
                pro_dic = parse_page(pro_url,headers)
                final_dic[kinds[i]][pro_dic['产品名称']] = pro_dic

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取完成，存储在{filename}中.')


if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    Damakawa_moter(headers=headers,filename='多摩川.json')