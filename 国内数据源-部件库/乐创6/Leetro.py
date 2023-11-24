import requests
from lxml import etree
import json
from urllib.parse import urljoin


def parse_page(pro_url,headers):
    pro_dic = {}
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@class="prod-tit"]/h3/text()')[0].strip()
    pro_info = tree.xpath('.//div[@class="prod-font"]//text()')
    pro_info = ''.join([item.strip() for item in pro_info])
    pro_img = urljoin(pro_url,tree.xpath('.//div[@class="prodimg-scroll fl"]//img/@src')[0]) 

    pro_desc,args = [],[]
    div_list = tree.xpath('.//div[@class="tab_box"]/div')
    desc_img = div_list[0].xpath('.//img')
    if desc_img != []:
        for img in desc_img:
            pro_desc.append(urljoin(pro_url,img.xpath('./@src')[0]))
    args_img = div_list[1].xpath('.//img')
    if args_img != '':
        for img in args_img:
            args.append(urljoin(pro_url,img.xpath('./@src')[0]))

    temp_dic = {'产品名称':pro_name,'产品信息':pro_info,'产品图片':pro_img,'产品介绍':pro_desc,'产品参数':args}
    pro_dic[pro_name] = temp_dic
    return pro_dic

def LEETRO(headers,filename='leetro.json'):
    final_dic = {}
    final_dic['电机控制器'] = {}
    final_dic['运动控制器'] = {}
    pro_urls = [
        'http://www.leetro.com/Product03/202306/2836.html',
        'http://www.leetro.com/Product02/202306/2832.html',
        'http://www.leetro.com/Product02/202306/2831.html',
        'http://www.leetro.com/Product02/202306/2833.html',
        'http://www.leetro.com/Product02/202306/2834.html',
        'http://www.leetro.com/Product02/202306/2835.html'
    ]

    for pro_url in pro_urls:
        print('当前的url是: ',pro_url)
        pro_dic = parse_page(pro_url,headers)
        if pro_urls.index(pro_url) == 0:
            final_dic['电机控制器'] |= pro_dic
        else:
            final_dic['运动控制器'] |= pro_dic           

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取完成，存储在{filename}中.')
    return final_dic

if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    LEETRO(headers=headers,filename='乐创.json')