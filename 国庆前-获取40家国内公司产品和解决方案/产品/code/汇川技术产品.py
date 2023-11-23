import re
import json
import requests
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_data(url,FirstType,SecondType):
    try:
        pro_list = []
        resp = requests.get(url=url,headers=headers)
        resp = resp.json()
        product_lists = resp.get('product')    
        for i in product_lists:
            for pro in product_lists[i]:
                pro_dic = {}
                productName = pro['productName']
                # logger.info(f'{productName}')
                characteristic = pro.get('characteristic')
                productFunDetail = pro.get('productFunDetail')      # 产品介绍
                productMainPic = pro.get('productMainPic')          # 产品图片
                productSpec = pro.get('productSpec')                # 产品参数
                detailParams = pro.get('detailParams')              # 特点详情
                productId = pro.get('productId')
                
                new_productMainPic = []
                # 处理产品图片
                if productMainPic:
                    productMainPic = productMainPic.split(',')
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

                # 处理产品特点
                detailParams1 = pro.get('detailParams1')
                if detailParams1:
                    characteristic = {}
                    for data in detailParams1:
                        characteristic[data['title']] = data['desc']
                else:
                    characteristic = {'text':characteristic}
                
                pro_dic['ProductName'] = productName
                pro_dic['ProductImage'] = new_productMainPic
                pro_dic['ProductUrl'] = f'https://www.inovance.com/portal/product/details?productId={productId}'
                pro_dic['ProductHTML'] = ''
                pro_dic['ProductJSON'] = pro
                pro_dic['FirstType'] = FirstType
                pro_dic['SecondType'] = SecondType
                pro_dic['ProductDetail'] = {}
                pro_dic['ProductDetail']['Description'] = productFunDetail
                pro_dic['ProductDetail']['Feature'] = characteristic
                pro_dic['ProductDetail']['Parameter'] = new_productSpec
                
                # logger.info(f'{new_detailParams}')
                # final_dic[productName]['产品优点'] = new_detailParams
                # detailTitle = pro['detailTitle']
                # detailDesc = pro['detailDesc']
                # if detailTitle and detailDesc :
                #     # final_dic[productName]['产品概览'] = detailDesc
                #     # logger.info(f'{detailDesc}')
                #     pass
                pro_list.append(pro_dic)
        return pro_list
    except Exception as e:
        logger.error(f'{e} URL: {url}')
        return None

if __name__ == '__main__': 
    logger.add('inovence.log',retention='1 day')
    all_dic = {'pro':[]}
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Cookie':'once=2023-9-11; Hm_lvt_df77af9ca30581ae15b09368240f63fc=1693819809; Hm_lpvt_df77af9ca30581ae15b09368240f63fc=1693820773',
        'Referer':'https://www.inovance.com/portal/product/details?productId=327'
    }

    resp = requests.Session().get('https://www.inovance.com/portal-front/api/home/getMenu',headers=headers)
    # logger.info(f'{resp.json}') # {'msg': '您发送请求的参数中含有非法字符', 'code': 500, 'time': '2023-09-26 11:33:15'}
    product = resp.json()['data']['product']
    for firstkind in product:
        typeName = firstkind['typeName']
        children = firstkind['children']
        if not children:
            continue
        for child in children:
            id = child['id']
            childtypeName = child['typeName']
            childurl = f'https://www.inovance.com/portal-front/api/product/type/list/{id}'
            all_dic['pro'] += get_data(childurl,typeName,childtypeName)
    '''
    urls = [
        'https://www.inovance.com/portal-front/api/product/type/list/7' ,  # 57 变频器
        'https://www.inovance.com/portal-front/api/product/type/list/13',  # 18 驱动器
        'https://www.inovance.com/portal-front/api/product/type/list/10',  # 29 电机
        'https://www.inovance.com/portal-front/api/product/type/list/30',  # 6  传感器
        'https://www.inovance.com/portal-front/api/product/type/list/26',  # 17 可编程逻辑控制器
        'https://www.inovance.com/portal-front/api/product/type/list/5' ,  # 1  人机交互
        'https://www.inovance.com/portal-front/api/product/type/list/200', #    PAC智能控制器
        'https://www.inovance.com/portal-front/api/product/type/list/221', #    CNC控制器
        'https://www.inovance.com/portal-front/api/product/type/list/202', #    柜机

    ]
    kinds = ['变频器','伺服','电机','传感器','可编程逻辑控制器','人机交互','PAC智能控制器','CNC控制器','柜机']
    for i in range(len(kinds)):
        all_dic['pro'] += get_data(urls[i],'工业自动化',kinds[i])
    
    urls = [
        'https://www.inovance.com/portal-front/api/product/type/list/227',  #    储能系统
        'https://www.inovance.com/portal-front/api/product/type/list/228',  #    工业电源
    ]
    kinds = ['储能系统','工业电源']
    for i in range(len(kinds)):
        all_dic['pro'] += get_data(urls[i],'能源',kinds[i])
    
    urls = [
        f'https://www.inovance.com/portal-front/api/product/type/list/{i}' for i in [95,99,100,103,104,212] 
    ]
    kinds = ['机器人系统','控制柜','机器人软件','机器人视觉系统','选配件','精密机械']
    for i in range(len(kinds)):
        all_dic['pro'] += get_data(urls[i],'工业机器人',kinds[i])
    
    urls = [
        f'https://www.inovance.com/portal-front/api/product/type/list/{i}' for i in [116,115,117,121,122,118,120]
    ]
    kinds = ['电梯控制柜','电梯一体化控制器','电梯专用变频器','门机一体化控制器','扶梯一体化控制器','电梯单板附件','电梯整机附件']
    for i in range(len(kinds)):
        all_dic['pro'] += get_data(urls[i],'智能电梯',kinds[i])

    urls = [
        f'https://www.inovance.com/portal-front/api/product/type/list/{i}' for i in [162,164,198]
    ]
    kinds = ['工业云平台','智能硬件','物联网屏']
    for i in range(len(kinds)):
        all_dic['pro'] += get_data(urls[i],'工业互联网',kinds[i])
    '''

    filename = '汇川技术.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'共爬取{len(all_dic["pro"])}条数据，存储在{filename}中.')