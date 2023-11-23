import httpx
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
    pro_name = tree.xpath('.//h1[1]/text()')[0].strip()
    pro_img = urljoin(pro_url,tree.xpath('.//div[@class="prod1_det_1"]//img/@src')[0])
    firstTypeName = tree.xpath('.//div[@class="det_crumbs"]/a[2]/text()')[0].strip()
    secondTypeName = tree.xpath('.//div[@class="det_crumbs"]/a[3]/text()')[0].strip()

    Description,Feature,Parameter = [],[],[]
    desp_text = tree.xpath('.//div[@class="prod1_det_1"]//text()')
    desp_text = ''.join([item.strip() for item in desp_text])
    if bool(desp_text):
        Description.append({'content':desp_text,'type':'text'})
    
    fea_text = tree.xpath('.//div[@class="det_point"]//text()')
    fea_text = ''.join([item.strip() for item in fea_text])
    if bool(fea_text):
        Feature.append({'content':fea_text,'type':'text'})
    fea_img_list = []
    fea_img_tree = tree.xpath('.//div[@class="det_point"]//img')
    for img in fea_img_tree:
        fea_img_list.append(urljoin(pro_url,img.xpath('./@src')[0]))
    if bool(fea_img_list):
        Feature.append({'content':fea_img_list,'type':'img'})
    
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
    pro_dic['ProductDetail']['Feature'] = Feature
    pro_dic['ProductDetail']['Parameter'] = Parameter
    return pro_dic

def YASKAWA(headers):
    final_dic = {'pro':[]}
    pro_urls = []
    # pro_urls = ['https://www.yaskawa.com.cn/product/product1_detail.aspx?id=37', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=40', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=38', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=12', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=16', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=4', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=18', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=44', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=43', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=42', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=41', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=20', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=7', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=19', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=17', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=8', 'https://www.yaskawa.com.cn/product/product1_detail.aspx?id=22']
    origion_url = 'https://www.yaskawa.com.cn/product/product1.aspx'
    resp = httpx.get(url=origion_url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    title = tree.xpath('.//title/text()')[0]
    logger.info(f'{title}')
    div_list = tree.xpath('.//div[@class="prod1_2"]//div[@class="item"]')
    for div in div_list:
        pro_urls.append(urljoin(origion_url,div.xpath('./a/@href')[0]))
    logger.info(f'{len(pro_urls)},{pro_urls}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for pro_url in pro_urls:
            future = executor.submit(parse_propage,pro_url)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            pro_dic = future.result()
            final_dic['pro'].append(pro_dic)
            logger.info(f'已爬取{len(final_dic["pro"])}/17条数据')
    return final_dic

if __name__ == '__main__':
    logger.add('kaifull.log')
    final_dic = {'pro':[]}
    # 运行时需更改Cookie,只能短时间使用1次
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'ASP.NET_SessionId=zrd3tleg0mhgy2tr4gp230ut; Hm_lvt_d34eed59da84795da57a49bf1192d4e1=1697170037,1699425702; Hm_lvt_373c48f58585db99ce21deaad9d59270=1697170037,1699425702; Hm_lvt_7b19abb7af2c1ac589a68e1220255915=1697170037,1699425702; HKIIUU9O618PPTHK=22956ad2a6cac8e0f35ada6520bf935a8a87270; Hm_lpvt_373c48f58585db99ce21deaad9d59270=1699426380; Hm_lpvt_d34eed59da84795da57a49bf1192d4e1=1699426380; Hm_lpvt_7b19abb7af2c1ac589a68e1220255915=1699426380; HKIIUU9O618PPTHP=MTY5OTQHyNjQwNzE3SkNhM3d3Z3YxcFlzeDFBMTgwczZTMzJoeHgxaD5l2MTE2aHUwNTE0dnNHaGJoMTR5cDE2dG843djZ4eG4xZCzRHM2s2YXdzQdTB08qd7Tk0a3g58aj1Q5MHQzeHh2djcwMnM2QTZydTcxaDY5MTgxMW5CMTNiNEpDYjBaODE3MWI1MDd0M2h6M3doM2g5NXVoaDk1c2szMGY1ajNzc2YwOTM4aDF4OEF1NHM5MzEzMjk2dGt0MzExaHoxMTFVaDhHcDExMWF2djg4bjVuaDEzZm5iMjExMXI4OG40aGhhMTExMTMwQ2o5bDFmN3k5OHQxemMxMTFoODAxZjg4U3d5MDIwNjMxOWcxNjhoaGV5SnRiM1Z6WlhnaU9pSXhNREF3TUNJc0ltMXZkWE5sZVNJNklqRXdNREF3SWl3aWMyTnlaV1Z1ZHlJNklqRTVNRE1pTENKelkzSmxaVzVvSWpvaU9URXhJaXdpYm05b1pXRmtaWElpT2lKdWJ5SXNJbTV2YldGc0lqb2llV1Z6SWl3aVlXcGhlQ0k2SW1GaFlXRmhJaXdpYm05M1gzVnVhWEYxWlNJNklqSXlPVFUyWVdReVlUWmpZV000WlRCbU16VmhaR0UyTlRJd1ltWTVNelZoT0dFNE56STNNQ0lzSW5Ob1pXSmxhU0k2SWxkbFlpSXNJbTVoZG1sbllYUnZjaUk2SW5abGJtUnZjbE4xWWowN2NISnZaSFZqZEZOMVlqMHlNREF6TURFd056dDJaVzVrYjNJOVIyOXZaMnhsSUVsdVl5NDdiV0Y0Vkc5MVkyaFFiMmx1ZEhNOU1EdHpZMmhsWkhWc2FXNW5QVnR2WW1wbFkzUWdVMk5vWldSMWJHbHVaMTA3ZFhObGNrRmpkR2wyWVhScGIyNDlOanRrYjA1dmRGUnlZV05yUFc1MWJHdzdaMlZ2Ykc5allYUnBiMjQ5VzI5aWFtVmpkQ0JIWlc5c2IyTmhkR2x2YmwwN1kyOXVibVZqZEdsdmJqMDVPM0JzZFdkcGJuTTlXMjlpYW1WamRDQlFiSFZuYVc1QmNuSmhlVjA3YldsdFpWUjVjR1Z6UFRFeE8zQmtabFpwWlhkbGNrVnVZV0pzWldROWRISjFaVHQzWldKcmFYUlVaVzF3YjNKaGNubFRkRzl5WVdkbFBURXpPM2RsWW10cGRGQmxjbk5wYzNSbGJuUlRkRzl5WVdkbFBURTBPMmhoY21SM1lYSmxRMjl1WTNWeWNtVnVZM2s5TVRJN1kyOXZhMmxsUlc1aFlteGxaRDEwY25WbE8yRndjRU52WkdWT1lXMWxQVTF2ZW1sc2JHRTdZWEJ3VG1GdFpUMU9aWFJ6WTJGd1pUdGhjSEJXWlhKemFXOXVQVEU1TzNCc1lYUm1iM0p0UFZkcGJqTXlPM0J5YjJSMVkzUTlSMlZqYTI4N2RYTmxja0ZuWlc1MFBUSXlPMnhoYm1kMVlXZGxQWHBvTFVOT08yeGhibWQxWVdkbGN6MTZhQzFEVGl4NmFEdHZia3hwYm1VOWRISjFaVHQzWldKa2NtbDJaWEk5Wm1Gc2MyVTdaMlYwUjJGdFpYQmhaSE05TWpjN2FtRjJZVVZ1WVdKc1pXUTlNamc3YzJWdVpFSmxZV052YmoweU9UdDJhV0p5WVhSbFBUTXdPMlJsY0hKbFkyRjBaV1JTZFc1QlpFRjFZM1JwYjI1RmJtWnZjbU5sYzB0QmJtOXVlVzFwZEhrOVptRnNjMlU3WW14MVpYUnZiM1JvUFZ0dlltcGxZM1FnUW14MVpYUnZiM1JvWFR0amJHbHdZbTloY21ROVcyOWlhbVZqZENCRGJHbHdZbTloY21SZE8yTnlaV1JsYm5ScFlXeHpQVE0wTzJ0bGVXSnZZWEprUFZ0dlltcGxZM1FnUzJWNVltOWhjbVJkTzIxaGJtRm5aV1E5TXpZN2JXVmthV0ZFWlhacFkyVnpQVE0zTzNOMGIzSmhaMlU5TXpnN2MyVnlkbWxqWlZkdmNtdGxjajB6T1R0MmFYSjBkV0ZzUzJWNVltOWhjbVE5TkRBN2QyRnJaVXh2WTJzOVcyOWlhbVZqZENCWFlXdGxURzlqYTEwN1pHVjJhV05sVFdWdGIzSjVQVGc3YVc1clBWdHZZbXBsWTNRZ1NXNXJYVHRvYVdROVcyOWlhbVZqZENCSVNVUmRPMnh2WTJ0elBWdHZZbXBsWTNRZ1RHOWphMDFoYm1GblpYSmRPMmR3ZFQxYmIySnFaV04wSUVkUVZWMDdiV1ZrYVdGRFlYQmhZbWxzYVhScFpYTTlORGM3YldWa2FXRlRaWE56YVc5dVBUUTRPM0JsY20xcGMzTnBiMjV6UFZ0dlltcGxZM1FnVUdWeWJXbHpjMmx2Ym5OZE8zQnlaWE5sYm5SaGRHbHZiajAxTUR0MWMySTlXMjlpYW1WamRDQlZVMEpkTzNoeVBWdHZZbXBsWTNRZ1dGSlRlWE4wWlcxZE8zTmxjbWxoYkQxYmIySnFaV04wSUZObGNtbGhiRjA3ZDJsdVpHOTNRMjl1ZEhKdmJITlBkbVZ5YkdGNVBUVTBPM1Z6WlhKQloyVnVkRVJoZEdFOU5UVTdZV1JCZFdOMGFXOXVRMjl0Y0c5dVpXNTBjejAxTmp0eWRXNUJaRUYxWTNScGIyNDlOVGM3WTJGdVRHOWhaRUZrUVhWamRHbHZia1psYm1ObFpFWnlZVzFsUFRVNE8yTmhibE5vWVhKbFBUVTVPM05vWVhKbFBUWXdPMk5zWldGeVFYQndRbUZrWjJVOU5qRTdaMlYwUW1GMGRHVnllVDAyTWp0blpYUlZjMlZ5VFdWa2FXRTlOak03Y21WeGRXVnpkRTFKUkVsQlkyTmxjM005TmpRN2NtVnhkV1Z6ZEUxbFpHbGhTMlY1VTNsemRHVnRRV05qWlhOelBUWTFPM05sZEVGd2NFSmhaR2RsUFRZMk8zZGxZbXRwZEVkbGRGVnpaWEpOWldScFlUMDJOenRrWlhCeVpXTmhkR1ZrVW1Wd2JHRmpaVWx1VlZKT1BUWTRPMlJsY0hKbFkyRjBaV1JWVWs1VWIxVlNURDAyT1R0blpYUkpibk4wWVd4c1pXUlNaV3hoZEdWa1FYQndjejAzTUR0cWIybHVRV1JKYm5SbGNtVnpkRWR5YjNWd1BUY3hPMnhsWVhabFFXUkpiblJsY21WemRFZHliM1Z3UFRjeU8zVndaR0YwWlVGa1NXNTBaWEpsYzNSSGNtOTFjSE05TnpNN2NtVm5hWE4wWlhKUWNtOTBiMk52YkVoaGJtUnNaWEk5TnpRN2RXNXlaV2RwYzNSbGNsQnliM1J2WTI5c1NHRnVaR3hsY2owM05TSjk@',
        'Referer':'https://www.yaskawa.com.cn/product/product3.aspx?id=p72339069014638592',
        'Host':'www.yaskawa.com.cn'
    }
    final_dic = YASKAWA(headers=headers)
    filename=f'安川电机产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    