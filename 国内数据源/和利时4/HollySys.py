import json
import requests
from lxml import etree
from urllib.parse import urljoin



def HollyController(headers,filename='HollySys.json'):
    holly_urls =[
        'https://www.hollysys.com/cn/content/details32_1652.html',
        'https://www.hollysys.com/cn/content/details32_1649.html',
        'https://www.hollysys.com/cn/content/details32_1528.html',
        'https://www.hollysys.com/cn/content/details32_336.html',
    ]
    final_dic = {}
    for url in holly_urls:
        resp = requests.get(url=url,headers=headers)
        resp.encoding = "utf-8"
        tree = etree.HTML(resp.text)
        pro_name = tree.xpath('/html/body/div[3]/div[2]/div[2]/div[1]/div[2]/h4/text()')[0]
        pro_intro = tree.xpath('/html/body/div[3]/div[2]/div[2]/div[1]/div[2]/p/text()')[0]
        pro_img = tree.xpath('//div[@class="swiper-slide"]/img/@src')[0]
        
        final_dic[pro_name] = {}
        final_dic[pro_name]['产品介绍'] = pro_intro
        final_dic[pro_name]['产品图片'] = pro_img
        final_dic[pro_name]['主要特性'] = []
        li_list = tree.xpath('/html/body/div[3]/div[2]/div[2]/div[2]/ul/li')
        for li in li_list:
            title = li.xpath('./h5//text()')[0]
            text1 = li.xpath('./p/text()')[0]
            text2 = li.xpath('./dl//text()')[0].strip()
            text = text1 + text2
            final_dic[pro_name]['主要特性'].append({title:text})
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    HollyController(headers=headers,filename='和利时.json')