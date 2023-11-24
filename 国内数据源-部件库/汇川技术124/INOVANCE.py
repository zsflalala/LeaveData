import requests
import re
import json
from urllib.parse import urljoin
import re


def get_data(url):
    final_dic = {}
    resp = requests.get(url=url,headers=headers)
    resp = resp.json()
    product_lists = resp['product']
    for i in product_lists:
        for pro in product_lists[i]:
            productName = pro['productName']
            final_dic[productName] = {}
            characteristic = pro['characteristic']
            productFunDetail = pro['productFunDetail']      # 产品介绍
            productMainPic = pro['productMainPic']          # 产品图片
            productSpec = pro['productSpec']                # 产品参数
            detailParams = pro['detailParams']              # 特点详情
            
            if not characteristic and not productFunDetail and not productMainPic:
                continue
            
            # 处理产品图片
            productMainPic = productMainPic.split(',')
            new_productMainPic = []
            for img in productMainPic:
                if img.startswith('/owfile'):
                    img = urljoin(url,img)
                new_productMainPic.append(img)

            # 处理产品参数
            if productSpec:
                ex = '<img src=\"(.*?)" alt='
                img_list = re.findall(ex,productSpec)
                if img_list != []:
                    new_productSpec = []
                    for img in img_list:
                        img = urljoin(url,img)
                        new_productSpec.append(img)
                else:
                    if productName == 'ES680N系列总线型电液伺服驱动器':
                        new_productSpec = None
                    new_productSpec = None
            else:
                new_productSpec = None

            # 处理产品优点
            if detailParams:
                pattern = re.compile("[\u4e00-\u9fa5]+")
                new_detailParams = {'Desc':','.join(pattern.findall(detailParams)),'img':[]}
                img_list = re.findall('\"img\":\"(.*?)"',detailParams)
                if img_list != []:
                    for img in img_list:
                        if img.strip():
                            img = urljoin(url,img)
                            new_detailParams['img'].append(img)
            else:
                new_detailParams = detailParams

            final_dic[productName]['产品特点'] = characteristic
            final_dic[productName]['产品介绍'] = productFunDetail
            final_dic[productName]['产品图片'] = new_productMainPic
            final_dic[productName]['产品参数'] = new_productSpec
            final_dic[productName]['产品优点'] = new_detailParams

            detailTitle = pro['detailTitle']
            detailDesc = pro['detailDesc']
            if detailTitle and detailDesc :
                final_dic[productName]['产品概览'] = detailDesc
    return final_dic


if __name__ == '__main__':   
    all_dic = {}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Cookie':'once=2023-9-11; Hm_lvt_df77af9ca30581ae15b09368240f63fc=1693819809; Hm_lpvt_df77af9ca30581ae15b09368240f63fc=1693820773',
        'Referer':'https://www.inovance.com/portal/product/details?productId=327'
    }
    urls = [
        'https://www.inovance.com/portal-front/api/product/type/list/7' , # 57 变频器
        'https://www.inovance.com/portal-front/api/product/type/list/13', # 14 驱动器
        'https://www.inovance.com/portal-front/api/product/type/list/10', # 23 电机
        'https://www.inovance.com/portal-front/api/product/type/list/30', # 6  传感器
        'https://www.inovance.com/portal-front/api/product/type/list/5' , # 1  人机界面HMI
        'https://www.inovance.com/portal-front/api/product/type/list/26'  # 17 控制器
    ]
    kinds = ['变频器','驱动器','电机','传感器','人机界面HMI','控制器']
    for i in range(6):
        all_dic[kinds[i]] = get_data(urls[i])
        
    filename = '汇川技术.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取完成，存储在{filename}中.')