import json
import requests
from lxml import etree
from urllib.parse import urljoin


def DemeterMotor(headers,filename='demeter_motor.json'):
    pro_urls,pro_names,pro_basics = [],[],[]
    for page in range (1,4):
        dmeter_url = f'http://www.sddemi.com/productlist.aspx?CategoryId=&pageindex={page}'
        resp = requests.get(dmeter_url,headers=headers)
        if resp.status_code != 200:
            print('状态码: ',resp.status_code)
            return None
        tree = etree.HTML(resp.text)
        div_lists = tree.xpath('//*[@id="productUnit"]')
        for div in div_lists:
            pro_name = div.xpath('./div[2]/a/span/text()')[0].strip().replace(' ','')
            pro_basic = div.xpath('./div[2]/div/span/text()')[0].strip().replace(' ','')
            pro_url = urljoin(dmeter_url,div.xpath('./div[2]/a/@href')[0]) 
            if pro_name.endswith('减速机') :
                continue
            pro_names.append(pro_name)
            pro_basics.append(pro_basic)
            pro_urls.append(pro_url)

    final_dic = {}
    for i in range(len(pro_urls)):
        pro_name,pro_basic,pro_url = pro_names[i],pro_basics[i],pro_urls[i]
        resp = requests.get(url=pro_url,headers=headers)
        tree = etree.HTML(resp.text)
        pro_img = urljoin(pro_url,tree.xpath('//*[@id="ContentPlaceHolder1_imgProduct"]/@src')[0])
        imgs = []
        print(pro_img)
        intro_imgs = tree.xpath('//*[@id="ContentPlaceHolder1_divProductContent"]//img')
        for img in intro_imgs:
            intro_img = urljoin(pro_url,img.xpath('./@src')[0])
            imgs.append(intro_img)
        
        title = tree.xpath('//*[@id="ContentPlaceHolder1_divProductContent"]//strong//text()')
        title = ''.join([item.strip() for item in title])
        pro_dic = { '产品信息':pro_basic,
                    '产品图片':pro_img,
                    '产品参数':imgs}
        final_dic[pro_name] = pro_dic

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")


if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    DemeterMotor(headers=headers,filename='德米特.json')
