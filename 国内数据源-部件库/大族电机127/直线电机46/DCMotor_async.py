import requests
from lxml import etree
import pandas as pd
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

# 协程太快了 会被封

def parse_table(tbdata,kind):
    table_dic = {}
    colunm_length = len(tbdata.columns.values.tolist())
    row_length = len(tbdata._stat_axis.values.tolist())

    if kind == 1:
        row = 2
        # 处理最左侧列名
        for i in range(3,row_length):
            tbdata.loc[i][0] += f" {tbdata.loc[2][1]}: {tbdata.loc[i][1]} ; {tbdata.loc[2][2]}: {tbdata.loc[i][2]}"

        for col in range(3,colunm_length):
            table_dic[tbdata.loc[1][col]] = {}
            while row < row_length:
                table_dic[tbdata.loc[1][col]][tbdata.loc[row][0]] = tbdata.loc[row][col]
                row += 1
            row = 2
        table_dic = {tbdata.loc[0][0]:{tbdata.loc[1][0]:table_dic}}
    elif kind == 2:
        row = 2
        while row < row_length:
            if str(tbdata.loc[row][0]) == 'nan':
                row += 1
                continue
            col = 1
            table_dic[tbdata.loc[row][0]] = {}
            while col < colunm_length:
                table_dic[tbdata.loc[row][0]][tbdata.loc[1][col]] = tbdata.loc[row][col]
                col += 1
            row += 1
        table_dic = {tbdata.loc[0][0]:{tbdata.loc[1][0]:table_dic}}
    elif kind == 3:
        for row in range(1,11,2):
            table_dic[tbdata.loc[row][0]] = {'设备':{'原设备':{},'大族LESP':{}}}
            for col in range(2,8):
                table_dic[tbdata.loc[row][0]]['设备']['原设备'][tbdata.loc[0,col]] = tbdata.loc[row,col]
                table_dic[tbdata.loc[row][0]]['设备']['大族LESP'][tbdata.loc[0,col]] = tbdata.loc[row+1,col]
        table_dic = {tbdata.loc[0][0]:table_dic}
    return table_dic


async def parse_linear_page(page_url,headers):
    # 产品标题 图片和特点
    async with asyncio.Semaphore(100):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=page_url,headers=headers) as response:
                tree = etree.HTML(await response.text())
                # tree = etree.HTML(requests.get(url=page_url,headers=headers).text)
                pro_name = tree.xpath('.//div[@class="base-info"]/div[1]/text()')[0].strip()
                pro_feature = tree.xpath('.//div[@class="base-info"]/div[3]//text()')
                pro_feature = ''.join([item.replace('\xa0','').strip() for item in pro_feature if item.strip()])
                pro_img = urljoin(page_url,tree.xpath('.//div[@class="img swiper-slide text-center"]/img/@src')[0])
                pro_basic = {'产品名称':pro_name,'产品特点':pro_feature,'产品图片':pro_img}
                # print(pro_name,pro_feature,pro_img)

                if pro_name == '汉士直线潜油电机':
                    # 产品介绍
                    img1 = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/img[1]/@src')[0])
                    img2 = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/img[2]/@src')[0])
                    img3 = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/img[3]/@src')[0])
                    pro_intro = {'img1':img1,'img2':img2,'img3':img3}

                    # 产品参数
                    tbdata = pd.read_html(page_url,encoding='utf-8')[0]
                    table_dic = parse_table(tbdata=tbdata,kind=3)

                    pro_args = {'table':table_dic}
                    pro_dic = {'基本信息':pro_basic,'产品介绍':pro_intro,'产品参数':pro_args}
                    return pro_dic

                # 产品介绍
                pro_intro = {}
                titles = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td//strong/text()')
                titles_len = len(titles)
                if titles_len:
                    first_title = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div[1]/strong/span/span/text()')[0]
                    first_title_content = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div[2]/span/text()')[0].strip()
                    if len(tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div[3]/strong/span/span/img/@src')) == 0:
                        first_title_img = ""
                    else:
                        first_title_img = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/div[3]/strong/span/span/img/@src')[0])
                    title_imgs = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td//img/@src')

                    second_title = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td/strong/span/span/text()')[0]
                    second_titles_content = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td/span//text()')
                    second_titles_content = [item.strip() for item in second_titles_content if item.strip()]

                    second_tilte1 = titles[0]
                    second_title1_content = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td/span[1]/text()')
                    second_title1_content = ''.join([item.strip() for item in second_title1_content])
                    second_title1_img = urljoin(page_url,title_imgs[0])
                    
                    second_tilte2 = titles[1]
                    second_title2_content = second_titles_content[-1]
                    second_title2_img = urljoin(page_url,title_imgs[1])
                
                    pro_intro[first_title],pro_intro[second_title] = {},{}
                    pro_intro[first_title] = {'text':first_title_content,'img':first_title_img}
                    pro_intro[second_title] = {second_tilte1:second_title1_content,'img1':second_title1_img,second_tilte2:second_title2_content,'img2':second_title2_img}
                else:
                    pro_intro = {'text':pro_feature}
                    

                print('产品参数===================',page_url)
                # 产品参数
                pro_args = {}

                if pro_name == '直线电机LSMA系列铁芯电机-自然冷却型':
                    img1 = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/img[1]/@src')[0])
                    img2 = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/img[2]/@src')[0])
                    pro_args['img1'] = img1
                    pro_args['img2'] = img2
                    pro_dic = {'基本信息':pro_basic,'产品介绍':pro_intro,'产品参数':pro_args}
                    return pro_dic

                first_txt = pro_name
                first_img = urljoin(page_url,tree.xpath('//div[@class="content c2"]//img/@src')[0])
                second_txt = first_txt.split('系列')[0] + '系列尺寸图'
                second_img = urljoin(page_url,tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]//img/@src')[0])
                print('second_txt',second_txt,second_img,'\n','first_txt',first_txt,first_img)
                
                tbdata = pd.read_html(page_url,encoding='utf-8')
                # table1
                if titles_len:
                    table1_dic = parse_table(tbdata[1],kind=1)
                    table2_dic = parse_table(tbdata[2],kind=2)
                    table3_dic = parse_table(tbdata[3],kind=2)

                    table2_txt = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/div[5]//text()')
                    table2_txt = ''.join([item.replace('\\xa0','').strip() for item in table2_txt])
                    table3_txt = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/div[7]/div//text()')
                    table3_txt = ''.join([item.replace('\\xa0','').strip() for item in table3_txt])
                else:
                    table1_dic = parse_table(tbdata[0],kind=1)
                    table2_dic = parse_table(tbdata[1],kind=2)
                    table3_dic = parse_table(tbdata[2],kind=2)
                    table2_txt = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/div[3]/div[1]//text()')
                    table2_txt = ''.join([item.replace('\\xa0','').strip() for item in table2_txt])
                    table3_txt = tree.xpath('/html/body/div[5]/div[2]/div[1]/div[2]/div[3]/div[1]/div[1]//text()')
                    table3_txt = ''.join([item.replace('\\xa0','').strip() for item in table3_txt])

                # print('table2 table3 txt : ',table2_txt,table3_txt)

                pro_args[first_txt] = {}
                pro_args[first_txt]['img'] = first_img
                pro_args[first_txt]['table'] = table1_dic
                pro_args[second_txt] = {}
                pro_args[second_txt]['img'] = second_img
                pro_args[second_txt]['table1'] = table2_dic
                pro_args[second_txt]['tbale1_txt'] = table2_txt
                pro_args[second_txt]['tbale2'] = table3_dic
                pro_args[second_txt]['tbale2_txt'] = table3_txt
                
                pro_dic = {'基本信息':pro_basic,'产品介绍':pro_intro,'产品参数':pro_args}
                return pro_dic

async def DCMotor(headers,filename='dcmotor.json'):
    final_dic = {}
    linear_url = 'https://www.hansmotor.com/products/1/c-1/'
    tree = etree.HTML(requests.get(url=linear_url,headers=headers).text)
    div_lists = tree.xpath('//div[@class="product-list"]/div/div[@class="box fl text-center relative"]')
    pro_urls,pro_names = [],[]
    for div in div_lists:
        pro_url = urljoin(linear_url,div.xpath('./div[3]//a/@href')[0])
        pro_name = div.xpath('./div[2]/text()')[0]
        pro_names.append(pro_name)
        pro_urls.append(pro_url)
    length = len(pro_urls)
    
    tasks = []

    for index in range(length):
        tasks.append(asyncio.create_task(parse_linear_page(page_url=pro_urls[index],headers=headers)))

    result = await asyncio.wait(tasks)
    # result = await asyncio.gather(*tasks,return_exceptions=True)
    for t in result:
        print(t)
        final_dic[pro_names[result.index(t)]] = t.result()

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f"爬取完成，存储在{filename}中.")

if __name__ == "__main__":
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    asyncio.run(DCMotor(headers=headers,filename='dcmotor.json'))
