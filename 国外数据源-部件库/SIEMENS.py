import re
import sys
import json
import requests
from lxml import etree

import os
import argparse
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

def parse_args():
    parser = argparse.ArgumentParser(description='部件库-B2B商城-国际-西门子官方商城')  # 2、创建参数对象
    parser.add_argument('-j', '--jsonFileName', default='temp.json', type=str, help='backup json file name')  # 3、往参数对象添加参数
    parser.add_argument('-e', '--errorFile', default='', type=str, help='error file name')
    parser.add_argument('-w', '--maxworker', default=10, type=int, help='threed pool max_worker')
    parser.add_argument('-de', '--isdealerror', default=False, type=bool, help='is needed to deal error file')
    args = parser.parse_args()  # 4、解析参数对象获得解析对象
    return args

def save_error(keyname,subobjName,skuNo,args):
    with open(file=args.errorFile,mode='a',encoding='utf-8') as f:
        f.write(f'{keyname},{subobjName},{skuNo}\n')
    return True

@logger.catch
def deal_error(args):
    try:
        keynameList,subobjNameList,skuNoList = [],[],[]
        with open(file=args.errorFile,mode='r',encoding='utf-8') as f:
            for line in f.readlines():
                keyname,subobjName,skuNo = line.strip().split(',')
                keynameList.append(keyname)
                subobjNameList.append(subobjName)
                skuNoList.append(skuNo)
        fileExists = os.path.isfile(args.errorFile)
        if fileExists:
            os.remove(args.errorFile)
        with ThreadPoolExecutor(max_workers=args.maxworker) as executor:
            to_do = []
            for i in range(len(skuNoList)):  # 模拟多个任务
                keyname,subobjName,skuNo = keynameList[i],subobjNameList[i],skuNoList[i]
                try:
                    future = executor.submit(get_proInfo, skuNo)
                    to_do.append(future)
                except Exception as e:
                    logger.exception(f'{e} 当前skuNo: {skuNo}')
                    isSave = save_error(keyname,subobjName,skuNo,args)
                    if isSave:
                        logger.debug(f'已存入{args.errorFile}')
            for future in concurrent.futures.as_completed(to_do):  # 并发执行
                pro_dic,skuNo = future.result()
                pro_dic = parse_proInfo(pro_dic,keyname,subobjName,skuNo)
                
                logger.info(f'已完成{keyname}--{subobjName}{skuNoList.index(skuNo)+1}/{len(skuNoList)},skuNo:{skuNo}')
            logger.info(f'{subobjName} have already done!')
    except Exception as e:
        logger.error(f'{e},please try again')
    return 0

# 获得一级目录名 - 二级目录名 + 二级目录的uuid
# 联合钜惠 没有二级类目，单独处理
@logger.catch
def get_proDic(url,headers):
    pro_dic = {}
    resp = requests.get(url=url,headers=headers)
    ex = '"l_1691131860410":(.*?),"l_1652790464515"'
    frontCategoryTree = re.findall(ex,resp.text)[0]
    frontCategoryTree = json.loads(frontCategoryTree)['backdata']['frontCategoryTree']
    for obj in frontCategoryTree:
        keyname = obj['categoryName'] 
        value = []
        if 'subList' in obj.keys():
            for subobj in obj['subList']:
                value.append([subobj['categoryName'],subobj['uuid']])
            pro_dic[keyname] = value
    return pro_dic

# 获得二级目录下所有产品的uuid
@logger.catch
def get_skuNo(uuid):
    Cookies = [
        'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%2C%22first_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22SLC%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD%22%2C%22%24latest_utm_medium%22%3A%22banner%22%2C%22%24latest_utm_campaign%22%3A%22%E4%BA%91%E4%B8%8A%E5%B0%8F%E5%BA%977%E5%91%A8%E5%B9%B4202308%22%2C%22%24latest_utm_content%22%3A%22%E9%A6%96%E9%A1%B5%22%2C%22%24latest_utm_term%22%3A%22%E8%A5%BF%E9%97%A8%E5%AD%90%E5%AE%98%E6%96%B9%E5%B7%A5%E4%B8%9A%E5%95%86%E5%9F%8E%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYTVkMmIzZjg0MWQtMGM1MmFhMWFkNDNlYTYtMjYwMzFmNTEtMjA3MzYwMC0xOGFhNWQyYjNmOTExY2YiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MzVmOGUxZTAzNzM0MTFmODhlOGQxOGEwOTVhNjhjYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%7D%2C%22%24device_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%7D; Hm_lvt_65765a77889259553c450a9f04bcf2a9=1694999165,1695014427; Hm_lvt_b62446f1c8e0965dd5717b699ed1683e=1694999165,1695019680; Hm_lpvt_b62446f1c8e0965dd5717b699ed1683e=1695019680; customer=; customerOut=52369; dcj-SessionId=ca387341-b4a6-43f9-b410-c0b2bf551bc0; Hm_lpvt_65765a77889259553c450a9f04bcf2a9=1695174820',
        'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%2C%22first_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22SLC%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD%22%2C%22%24latest_utm_medium%22%3A%22banner%22%2C%22%24latest_utm_campaign%22%3A%22%E4%BA%91%E4%B8%8A%E5%B0%8F%E5%BA%977%E5%91%A8%E5%B9%B4202308%22%2C%22%24latest_utm_content%22%3A%22%E9%A6%96%E9%A1%B5%22%2C%22%24latest_utm_term%22%3A%22%E8%A5%BF%E9%97%A8%E5%AD%90%E5%AE%98%E6%96%B9%E5%B7%A5%E4%B8%9A%E5%95%86%E5%9F%8E%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYTVkMmIzZjg0MWQtMGM1MmFhMWFkNDNlYTYtMjYwMzFmNTEtMjA3MzYwMC0xOGFhNWQyYjNmOTExY2YiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MzVmOGUxZTAzNzM0MTFmODhlOGQxOGEwOTVhNjhjYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%7D%2C%22%24device_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%7D; Hm_lvt_65765a77889259553c450a9f04bcf2a9=1694999165,1695014427; Hm_lvt_b62446f1c8e0965dd5717b699ed1683e=1694999165,1695019680; Hm_lpvt_b62446f1c8e0965dd5717b699ed1683e=1695019680; Hm_lpvt_65765a77889259553c450a9f04bcf2a9=1695173230; customer=; customerOut=52369; dcj-SessionId=88c8d324-1d98-4634-a74f-194dce6a2c30',
        'customer=; customerOut=53637; sajssdk_2015_cross_new_user=1; Hm_lvt_65765a77889259553c450a9f04bcf2a9=1694999165; Hm_lvt_b62446f1c8e0965dd5717b699ed1683e=1694999165; dcj-SessionId=86d24620-bde2-4e6d-8ad5-3651423883c8; rememberMe=c1F/vk8I/efHgRduwH8eQ+I0XgHOEPpWGTTGmSn/ClFdnos4Vle4rM32qkAbi/7UHi0/8tePn9p+2oBWcfhyo89Hta3qX0feYjO7V8SRzPy5VIPz8za0QnC0smbm8qZx74sHxOivqgyxvtNn5KK3JEczWH1Zb5j3OpS3fzUyFxI71p3843AuxNi24RERHrT82vYMWmPKSVD7owDKRnANFZ1SWLE6WULKvDsuHEarzFg+wxJ8M06nal9cNELAWMJTwSVsQjFDyaX2qoIGDjoDEkICZxPNNNZojKGEX6roAyXnS3pdPHMb1bsNMoTfHvl3SU/SbOB4kbqlyeS2pbKqo1WGAi8bO5ucbMjgxFEhZMpy22bUJlS3+2bGNNHO0CJ2DTt5Ho5oSJ4hpHZTf6WpJpwTdqucupxe2BU+KkpbBKG18tSGiKUCL0Fw6sJoSsdtcftdSVhTVuD3Wm/exmRAMH1XDCoEp87DjQBuLNX8icY8Qyim6Sj6AQe68/1nma+43DeTlJcAYwODfufTeMGLInGyVTOUPlw3NxY9jV0i2mvUFdG+VnZcqvVj; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%2C%22first_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22SLC%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD%22%2C%22%24latest_utm_medium%22%3A%22banner%22%2C%22%24latest_utm_campaign%22%3A%22%E4%BA%91%E4%B8%8A%E5%B0%8F%E5%BA%977%E5%91%A8%E5%B9%B4202308%22%2C%22%24latest_utm_content%22%3A%22%E9%A6%96%E9%A1%B5%22%2C%22%24latest_utm_term%22%3A%22%E8%A5%BF%E9%97%A8%E5%AD%90%E5%AE%98%E6%96%B9%E5%B7%A5%E4%B8%9A%E5%95%86%E5%9F%8E%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYTVkMmIzZjg0MWQtMGM1MmFhMWFkNDNlYTYtMjYwMzFmNTEtMjA3MzYwMC0xOGFhNWQyYjNmOTExY2YiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MzVmOGUxZTAzNzM0MTFmODhlOGQxOGEwOTVhNjhjYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%7D%2C%22%24device_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%7D; Hm_lpvt_b62446f1c8e0965dd5717b699ed1683e=1695004131; Hm_lpvt_65765a77889259553c450a9f04bcf2a9=1695004885',
    ]
    url = 'https://mall.siemens.com.cn/front/productlist/search'
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Cookie':'customer=; customerOut=53637; sajssdk_2015_cross_new_user=1; Hm_lvt_65765a77889259553c450a9f04bcf2a9=1694999165; Hm_lvt_b62446f1c8e0965dd5717b699ed1683e=1694999165; dcj-SessionId=86d24620-bde2-4e6d-8ad5-3651423883c8; rememberMe=c1F/vk8I/efHgRduwH8eQ+I0XgHOEPpWGTTGmSn/ClFdnos4Vle4rM32qkAbi/7UHi0/8tePn9p+2oBWcfhyo89Hta3qX0feYjO7V8SRzPy5VIPz8za0QnC0smbm8qZx74sHxOivqgyxvtNn5KK3JEczWH1Zb5j3OpS3fzUyFxI71p3843AuxNi24RERHrT82vYMWmPKSVD7owDKRnANFZ1SWLE6WULKvDsuHEarzFg+wxJ8M06nal9cNELAWMJTwSVsQjFDyaX2qoIGDjoDEkICZxPNNNZojKGEX6roAyXnS3pdPHMb1bsNMoTfHvl3SU/SbOB4kbqlyeS2pbKqo1WGAi8bO5ucbMjgxFEhZMpy22bUJlS3+2bGNNHO0CJ2DTt5Ho5oSJ4hpHZTf6WpJpwTdqucupxe2BU+KkpbBKG18tSGiKUCL0Fw6sJoSsdtcftdSVhTVuD3Wm/exmRAMH1XDCoEp87DjQBuLNX8icY8Qyim6Sj6AQe68/1nma+43DeTlJcAYwODfufTeMGLInGyVTOUPlw3NxY9jV0i2mvUFdG+VnZcqvVj; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%2C%22first_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22SLC%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD%22%2C%22%24latest_utm_medium%22%3A%22banner%22%2C%22%24latest_utm_campaign%22%3A%22%E4%BA%91%E4%B8%8A%E5%B0%8F%E5%BA%977%E5%91%A8%E5%B9%B4202308%22%2C%22%24latest_utm_content%22%3A%22%E9%A6%96%E9%A1%B5%22%2C%22%24latest_utm_term%22%3A%22%E8%A5%BF%E9%97%A8%E5%AD%90%E5%AE%98%E6%96%B9%E5%B7%A5%E4%B8%9A%E5%95%86%E5%9F%8E%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYTVkMmIzZjg0MWQtMGM1MmFhMWFkNDNlYTYtMjYwMzFmNTEtMjA3MzYwMC0xOGFhNWQyYjNmOTExY2YiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MzVmOGUxZTAzNzM0MTFmODhlOGQxOGEwOTVhNjhjYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%7D%2C%22%24device_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%7D; Hm_lpvt_b62446f1c8e0965dd5717b699ed1683e=1695004131; Hm_lpvt_65765a77889259553c450a9f04bcf2a9=1695004885',
        # 'Cookie':'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%2C%22first_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22SLC%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD%22%2C%22%24latest_utm_medium%22%3A%22banner%22%2C%22%24latest_utm_campaign%22%3A%22%E4%BA%91%E4%B8%8A%E5%B0%8F%E5%BA%977%E5%91%A8%E5%B9%B4202308%22%2C%22%24latest_utm_content%22%3A%22%E9%A6%96%E9%A1%B5%22%2C%22%24latest_utm_term%22%3A%22%E8%A5%BF%E9%97%A8%E5%AD%90%E5%AE%98%E6%96%B9%E5%B7%A5%E4%B8%9A%E5%95%86%E5%9F%8E%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYTVkMmIzZjg0MWQtMGM1MmFhMWFkNDNlYTYtMjYwMzFmNTEtMjA3MzYwMC0xOGFhNWQyYjNmOTExY2YiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MzVmOGUxZTAzNzM0MTFmODhlOGQxOGEwOTVhNjhjYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%7D%2C%22%24device_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%7D; Hm_lvt_65765a77889259553c450a9f04bcf2a9=1694999165,1695014427; Hm_lvt_b62446f1c8e0965dd5717b699ed1683e=1694999165,1695019680; Hm_lpvt_b62446f1c8e0965dd5717b699ed1683e=1695019680; Hm_lpvt_65765a77889259553c450a9f04bcf2a9=1695173230; customer=; customerOut=52369; dcj-SessionId=88c8d324-1d98-4634-a74f-194dce6a2c30',
        'Referer':'https://mall.siemens.com.cn/pcweb/detailIndex/2100000539.html',
        'Content-Type':'application/json; charset=UTF-8'
    }
    
    try_data = {"nowPage":'1',"pageShow":1,"specList":[],"sortName":"","sortType":"asc","originalPriceStart":"","originalPriceEnd":"","keyword":None,
            "frontCategoryUuid":f"{uuid}","contentUuid":"","contentType":"","isAsp":"0"}
    data = json.dumps(try_data)
    resp = requests.post(url=url,headers=headers,data=data)
    retData = resp.json()['retData']
    retData = json.loads(retData)
    totalNum = int(retData['totalNum'])

    stuNoList = []
    for nowPage in range(1,totalNum // 5000 + 2):
        data = {"nowPage":f"{nowPage}","pageShow":5000,"specList":[],"sortName":"","sortType":"asc","originalPriceStart":"","originalPriceEnd":"","keyword":None,
                "frontCategoryUuid":f"{uuid}","contentUuid":"","contentType":"","isAsp":"0"}
        data = json.dumps(data)
        resp = requests.post(url=url,headers=headers,data=data)
        retData = resp.json()['retData']
        retData = json.loads(retData)
        skuList = retData['skuList']
        for sku in skuList:
            skuNo = sku['skuNo']
            stuNoList.append(skuNo)
    return stuNoList

# 获得二级目录下单条产品的信息
@logger.catch
def get_proInfo(skuNo=2100000539):
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Cookie':'customer=; customerOut=53637; sajssdk_2015_cross_new_user=1; Hm_lvt_65765a77889259553c450a9f04bcf2a9=1694999165; Hm_lvt_b62446f1c8e0965dd5717b699ed1683e=1694999165; dcj-SessionId=86d24620-bde2-4e6d-8ad5-3651423883c8; rememberMe=c1F/vk8I/efHgRduwH8eQ+I0XgHOEPpWGTTGmSn/ClFdnos4Vle4rM32qkAbi/7UHi0/8tePn9p+2oBWcfhyo89Hta3qX0feYjO7V8SRzPy5VIPz8za0QnC0smbm8qZx74sHxOivqgyxvtNn5KK3JEczWH1Zb5j3OpS3fzUyFxI71p3843AuxNi24RERHrT82vYMWmPKSVD7owDKRnANFZ1SWLE6WULKvDsuHEarzFg+wxJ8M06nal9cNELAWMJTwSVsQjFDyaX2qoIGDjoDEkICZxPNNNZojKGEX6roAyXnS3pdPHMb1bsNMoTfHvl3SU/SbOB4kbqlyeS2pbKqo1WGAi8bO5ucbMjgxFEhZMpy22bUJlS3+2bGNNHO0CJ2DTt5Ho5oSJ4hpHZTf6WpJpwTdqucupxe2BU+KkpbBKG18tSGiKUCL0Fw6sJoSsdtcftdSVhTVuD3Wm/exmRAMH1XDCoEp87DjQBuLNX8icY8Qyim6Sj6AQe68/1nma+43DeTlJcAYwODfufTeMGLInGyVTOUPlw3NxY9jV0i2mvUFdG+VnZcqvVj; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%2C%22first_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22SLC%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD%22%2C%22%24latest_utm_medium%22%3A%22banner%22%2C%22%24latest_utm_campaign%22%3A%22%E4%BA%91%E4%B8%8A%E5%B0%8F%E5%BA%977%E5%91%A8%E5%B9%B4202308%22%2C%22%24latest_utm_content%22%3A%22%E9%A6%96%E9%A1%B5%22%2C%22%24latest_utm_term%22%3A%22%E8%A5%BF%E9%97%A8%E5%AD%90%E5%AE%98%E6%96%B9%E5%B7%A5%E4%B8%9A%E5%95%86%E5%9F%8E%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYTVkMmIzZjg0MWQtMGM1MmFhMWFkNDNlYTYtMjYwMzFmNTEtMjA3MzYwMC0xOGFhNWQyYjNmOTExY2YiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MzVmOGUxZTAzNzM0MTFmODhlOGQxOGEwOTVhNjhjYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22535f8e1e0373411f88e8d18a095a68cc%22%7D%2C%22%24device_id%22%3A%2218aa5d2b3f841d-0c52aa1ad43ea6-26031f51-2073600-18aa5d2b3f911cf%22%7D; Hm_lpvt_b62446f1c8e0965dd5717b699ed1683e=1695004131; Hm_lpvt_65765a77889259553c450a9f04bcf2a9=1695004885',
        'Referer':'https://mall.siemens.com.cn/pcweb/detailIndex/2100000539.html',
    }
    url = f'https://mall.siemens.com.cn/front/productdetail/getProductDetailBySkuNo?skuNo={skuNo}'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    retData = resp.json()['retData']
    retData = json.loads(retData)
    return retData,skuNo

# 处理产品信息
@logger.catch
def parse_proInfo(pro_dic,first_type,second_type,skuNo):
    new_pro_dic = {}
    new_pro_dic['url'] =  f'https://mall.siemens.com.cn/pcweb/detailIndex/{skuNo}.html'
    new_pro_dic['first_type'] = first_type
    new_pro_dic['second_type'] = second_type
    new_pro_dic['产品名称'],new_pro_dic['产品图片'] = '',''
    down_proxie = 'https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/'
    productName = pro_dic['productName']
    basicImageKey = pro_dic['basicImageKey']
    basicImageKey = json.loads(basicImageKey)
    if basicImageKey != {}:
        productImage =  down_proxie + basicImageKey['imageKey']
        new_pro_dic['产品名称'],new_pro_dic['产品图片'] = productName,productImage
    else:
        cateRelCoverImageKey = pro_dic.get('cateRelCoverImageKey')
        if cateRelCoverImageKey:
            productImage =  down_proxie + cateRelCoverImageKey
            new_pro_dic['产品名称'],new_pro_dic['产品图片'] = productName,productImage

    new_pro_dic['产品视频'] = {}
    if 'videoKey' in pro_dic.keys():
        new_pro_dic['产品视频'] = down_proxie + pro_dic['videoKey']

    # 基本信息
    new_pro_dic['基本信息'] = {}
    specAttrDTOList = pro_dic.get('specAttrDTOList')
    if specAttrDTOList:
        for attribute in specAttrDTOList:
            attrShowName = attribute['attrShowName']
            attrValueName = attribute['attrValueName']
            new_pro_dic['基本信息'][attrShowName] = attrValueName
    
    # 产品详情
    new_pro_dic['产品详情'] = {}
    new_pro_dic['产品详情']['image'],new_pro_dic['产品详情']['video'] = [],[]
    new_pro_dic['买家必读'] = 'https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2021/11/17/FILEfe3ed29ffe78413492b00e04112236e1.jpg'
    new_pro_dic['3D模型'],new_pro_dic['产品参数'] = '',''
    new_pro_dic['资料下载'] = {'产品样本':'','技术参数':''}
    descTabRelModelList = pro_dic['descTabRelModelList']
    for descModel in descTabRelModelList:
        tabName = descModel['tabName']
        if tabName == '买家必读':
            continue
        elif tabName == '产品详情':
            Content = descModel['describeContent']
            tree = etree.HTML(Content)
            img_tree = tree.xpath('.//img/@src')
            if img_tree != []:
                for img in img_tree:
                    new_pro_dic['产品详情']['image'].append(img)
            video_tree = tree.xpath('.//video/@src')
            if video_tree != []:
                for video in video_tree:
                    new_pro_dic['产品详情']['video'].append(video)
        elif tabName == '3D模型':
            resourcesUrl = descModel['resourcesUrl']
            new_pro_dic['3D模型'] = 'https://dcj-3dview.siemens.com.cn/?environment=pro&filePath=' + resourcesUrl
        elif tabName == '产品参数':
            paramsContent = descModel.get('paramsContent')
            if paramsContent:
                new_pro_dic['产品参数'] = 'https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/' + paramsContent
        elif tabName == '资料下载':
            dataUrl1 = descModel.get('dataUrl1')
            dataUrl2 = descModel.get('dataUrl2')
            if dataUrl1:
                sample = 'https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/' + dataUrl1
                new_pro_dic['资料下载'] |= {'产品样本':sample}
            if dataUrl2:
                technic = 'https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/' + dataUrl2
                new_pro_dic['资料下载'] |= {'技术参数':technic}

    # 产品参数的表格
    new_pro_dic['基本参数'] = {}
    noSpecAttrDTOList = pro_dic.get('noSpecAttrDTOList')
    if noSpecAttrDTOList:
        for attr in noSpecAttrDTOList:
            attributeName = attr['attributeName']
            valueName = attr['attrValues'][0]['valueName']
            new_pro_dic['基本参数'][attributeName] = valueName
    return new_pro_dic

@logger.catch
def crawlab_main(args):
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    url = 'https://mall.siemens.com.cn/'
    pro_dic = get_proDic(url=url,headers=headers)
    
    final_dic = {'pro':[]}
    # 包含二级类目产品
    # 1.查找所有二级产品下的skuNo
    for keyname,value in pro_dic.items():
        if keyname != '工业驱动技术' and keyname != '工业自动化系统':
            logger.info(f"{keyname} begin======>")
            for subobj in value:
                subobjName = subobj[0]
                subobjUuid = subobj[1]
                skuNoList = get_skuNo(uuid=subobjUuid)
                with ThreadPoolExecutor(max_workers=args.maxworker) as executor:
                    to_do = []
                    for i in range(len(skuNoList)):  # 模拟多个任务
                        skuNo = skuNoList[i]
                        try:
                            future = executor.submit(get_proInfo, skuNo)
                            to_do.append(future)
                        except Exception as e:
                            logger.exception(f'{e} 当前skuNo: {skuNo}')
                            isSave = save_error(keyname,subobjName,skuNo,args)
                            if isSave:
                                logger.debug(f'已存入{args.errorFile}')
                    for future in concurrent.futures.as_completed(to_do):  # 并发执行
                        pro_dic,skuNo = future.result()
                        pro_dic = parse_proInfo(pro_dic,keyname,subobjName,skuNo)
                        final_dic['pro'].append(pro_dic) 
                        logger.info(f'已完成{keyname}--{subobjName}{skuNoList.index(skuNo)+1}/{len(skuNoList)},skuNo:{skuNo}')
                    logger.info(f'{subobjName} have already done!')
    
    # 联合钜惠
    keyname = '联合钜惠'
    skuNoList = get_skuNo(uuid='732aa9ba63ff4be8a167fd35b4df85c9')
    with ThreadPoolExecutor(max_workers=args.maxworker) as executor:
        to_do = []
        for i in range(len(skuNoList)):  # 模拟多个任务
            skuNo = skuNoList[i]
            try:
                future = executor.submit(get_proInfo, skuNo)
                to_do.append(future)
            except Exception as e:
                logger.exception(f'{e} 当前skuNo: {skuNo}')
                isSave = save_error(keyname,subobjName,skuNo,args)
                if isSave:
                    logger.debug(f'已存入{args.errorFile}')
        for future in concurrent.futures.as_completed(to_do):  # 并发执行
            pro_dic,skuNo = future.result()
            pro_dic = parse_proInfo(pro_dic,keyname,'',skuNo)
            final_dic['pro'].append(pro_dic) 
            logger.info(f'已完成{keyname}{skuNoList.index(skuNo)+1}/{len(skuNoList)}')
        logger.info(f'{keyname} have already done!')
    
    filename,dic = args.jsonFileName,final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'爬取完成，存储在{filename}中.')
    return 0 

if __name__ =='__main__':
    args = parse_args()
    logger.add(sys.stderr,format="{time} {level} {message}",filter="my_module", level="INFO")
    logger.add("runtime.log",retention="1 day")
    if args.isdealerror:
        deal_error(args)
    else:
        crawlab_main(args)

    
