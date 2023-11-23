import requests
from lxml import etree
import json
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

def parse_page(url,headers):
    pro_dic = {}
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    pro_name = tree.xpath('.//div[@id="proInfo"]/h1/text()')[0]
    pro_img = tree.xpath('.//div[@class="mainfigure"]/img/@src')[0]
    pro_desc = tree.xpath('.//div[@class="postmeta"]//text()')[0]
    pro_desc = ''.join([item.strip() for item in pro_desc])

    detail_img = []
    detail_img_tree = tree.xpath('.//div[@class="baguetteBox protfolio advantage"]//img')
    if detail_img_tree != []:
        for img in detail_img_tree:
            detail_img.append(img.xpath('./@src')[0])

    pro_info = {}
    info_text = tree.xpath('.//div[@class="entry"]//text()')
    info_text = ''.join([item.strip() for item in info_text])
    info_imgs = []
    info_img_tree = tree.xpath('.//div[@class="entry"]//img')
    if info_img_tree != []:
        for img in info_img_tree:
            info_imgs.append(img.xpath('./@src')[0])
    pro_info['text'] = info_text
    pro_info['img'] = info_imgs
    
    pro_dic['产品名称'] = pro_name
    pro_dic['产品链接'] = url
    pro_dic['产品介绍'] = pro_desc
    pro_dic['产品图片'] = pro_img
    pro_dic['细节图片'] = detail_img
    pro_dic['详细描述'] = pro_info
    return pro_dic

# 网页中无法打开产品类别主页 只能试出产品链接
def search_pro_url(url,headers,pro_names,pro_urls):
    resp = requests.get(url=url,headers=headers)
    tree = etree.HTML(resp.text)
    notfound = tree.xpath('.//div[@class="notfound"]')
    if notfound == []:
        proInfo = tree.xpath('.//div[@id="proInfo"]')
        if proInfo != []:
            pro_name = tree.xpath('.//div[@id="proInfo"]/h1/text()')[0]
            if '滑动轴承' not in pro_name and '可代替' not in pro_name:
                pro_names.append(pro_name)
                pro_urls.append(url)
                print(pro_name," ",url)
    
def get_pro_url(pro_names,pro_urls):
    with ThreadPoolExecutor(100) as t:
        for id in range(200,400):
            url = f'http://www.teco-motors.com/post/{id}.html'
            t.submit(search_pro_url,url,headers,pro_names,pro_urls)
        for id in range(4300,5400):
            url = f'http://www.teco-motors.com/post/{id}.html'
            t.submit(search_pro_url,url,headers,pro_names,pro_urls)
    return

def DONTYUAN(headers,filename='dongyuan.json'):
    pro_names,pro_urls = [],[]
    final_dic = {}
    # get_pro_url(pro_names,pro_urls)
    with open('temp.txt','r',encoding='utf-8') as f:
        pro_names = f.readline().split(',')
        pro_urls = f.readline().split(',')
    print(len(pro_urls))
    # for i in range(len(pro_urls)):
    #     final_dic[pro_names[i]] = parse_page(pro_urls[i],headers)
    to_do = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(len(pro_urls)):  # 模拟多个任务
            future = executor.submit(parse_page, pro_urls[i],headers)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):  # 并发执行
            final_dic[future.result()['产品名称']] = future.result()

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")
    return

if __name__ == '__main__':
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    DONTYUAN(headers=headers,filename='东元电机.json')
        
    
    

