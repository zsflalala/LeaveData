from urllib.parse import urljoin
import pandas as pd
import json
import requests
from lxml import etree

url_based = 'http://www.coolmay.com'
end_list_json_PLC_K = []
end_list_json_HIMI = []
end_list_json_PLC = []
from requests.exceptions import RequestException
import time


def re_txt(url):
    while True:
        try:
            r = requests.get(url, timeout=20)
            return r
        except RequestException:
            time.sleep(1)
            print("超时20S，重新请求中")

            continue


# HIMI人机界面
def get1_HIMI(url):
    resp = re_txt(url)

    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]

    Product_img = urljoin(url_based, Product_img)
    # 1

    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features_end = ''.join([item.strip() for item in Product_Features if item.strip()])

    # 2

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)
    # 添加图片
    #
    #
    url_two_2 = \
    tree.xpath("//*[@id='tabs_pro']/div[2]/samp[2]/div/div/table/tbody/tr[27]/td[2]/p/span[2]/span[2]/a/@href")[0]
    for key, value in dict_list[-1].items():
        if int(key) > 1:
            value = value + ':' + url_two_2
            dict_list[-1][key] = value

    name_list = []
    new_dic = {}
    new_new_dic = {}
    time_dic = {}
    end_dic = {}
    time_key = '规格'
    mid_dic = {}
    mid_end_dic = {}
    for key, value in dict_list[0].items():
        if '产品类型' not in value:
            name_list.append(value)
    for i in range(0, len(name_list)):
        for k in range(1, len(dict_list)):
            for count in range(1, 8):
                key = dict_list[k]['1']
                value = dict_list[k][f'{count}']
                new_dic[key] = value

                if dict_list[k]['0'] != dict_list[k]['1']:
                    key = dict_list[k]['0']
                    if time_key == key:
                        mid_end_dic = {**mid_dic, **new_dic}
                    else:
                        new_new_dic[time_key] = mid_end_dic
                        time_key = key
                        new_dic = {}
                    new_new_dic[time_key] = mid_end_dic
                else:
                    new_new_dic = {**new_new_dic, **new_dic}

        key = name_list[i]
        value = new_new_dic
        end_dic[key] = value
    kkk_dic = {}
    kkk_dic['产品类型'] = end_dic

    Installation_dimensions_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions_url)
    product_name = 'TK系列触摸屏人机界面（渠道）'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                "基本参数": kkk_dic, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_HIMI.append(end_dict_end)
    # with open(f'HMI人机界面.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get2_HIMI(url):
    resp = re_txt(url)

    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features_end = ''.join([item.strip() for item in Product_Features if item.strip()])

    # 2

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)

    # 添加图片
    #
    #
    url_two_2 = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[2]/div/table/tbody/tr[27]/td[2]/p/span[2]/span[2]/a/@href')[
        0]

    for key, value in dict_list[-1].items():
        if int(key) > 1:
            value = value + ':' + url_two_2
            dict_list[-1][key] = value

    name_list = []
    new_dic = {}
    new_new_dic = {}
    time_dic = {}
    end_dic = {}
    time_key = '规格'
    mid_dic = {}
    mid_end_dic = {}
    for key, value in dict_list[0].items():
        if '产品类型' not in value:
            name_list.append(value)
    for i in range(0, len(name_list)):
        for k in range(1, len(dict_list)):
            for count in range(1, 8):
                key = dict_list[k]['1']
                value = dict_list[k][f'{count}']
                new_dic[key] = value

                if dict_list[k]['0'] != dict_list[k]['1']:
                    key = dict_list[k]['0']
                    if time_key == key:
                        mid_end_dic = {**mid_dic, **new_dic}
                    else:
                        new_new_dic[time_key] = mid_end_dic
                        time_key = key
                        new_dic = {}
                    new_new_dic[time_key] = mid_end_dic
                else:
                    new_new_dic = {**new_new_dic, **new_dic}

        key = name_list[i]
        value = new_new_dic
        end_dic[key] = value
    kkk_dic = {}
    kkk_dic['产品类型'] = end_dic

    Installation_dimensions_url = '无'
    product_name = 'TP系列触摸屏人机界面'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                "基本参数": kkk_dic, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_HIMI.append(end_dict_end)
    # with open(f'HMI人机界面.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get3_HIMI(url):
    resp = re_txt(url)

    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features_end = ''.join([item.strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[1]/span/strong/a/@href')[0]

    Product_Features_end = '购买链接：' + buy_url + '，' + Product_Features_end

    # 2
    picture_url = tree.xpath(
        '//*[@id="tabs_pro"]/div[2]/samp[2]/table/tbody/tr[position()<4]//a/@href' or '//*[@id="tabs_pro"]/div[2]/samp[2]/table/tbody/tr[position()<4]//img/@src')

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)

    # 添加图片
    for i in range(0, len(picture_url)):
        for key, value in dict_list[0].items():
            if key != '产品类型' and key != '产品类型.1':
                dict_list[0][key] = [picture_url[i]]
    for i in range(5, len(picture_url)):
        for key, value in dict_list[1].items():
            if key != '产品类型' and key != '产品类型.1':
                dict_list[1][key] = [picture_url[i]]

    thing_name = []
    new_dic = {}
    new_new_dic = {}
    new_3_dic = {}
    for key, value in dict_list[0].items():
        if '产品类型' not in key:
            name = key
            thing_name.append(name)
    key_new_one = '产  品  图  片'
    for k in thing_name:
        for i in range(0, len(dict_list)):
            if key_new_one != dict_list[i]['产品类型'] and i != 0:
                if key_new_one == key_new:
                    new_new_dic[key_new_one] = value_new
                else:
                    new_new_dic[key_new_one] = new_dic
                new_dic = {}
                key_new_one = dict_list[i]['产品类型']
                key_new = dict_list[i]['产品类型.1']
                value_new = dict_list[i][f'{k}']
                new_dic[key_new] = value_new

            else:
                key_new_one = dict_list[i]['产品类型']
                key_new = dict_list[i]['产品类型.1']
                value_new = dict_list[i][f'{k}']
                new_dic[key_new] = value_new
        if new_dic != {}:
            new_new_dic[key_new_one] = new_dic[key_new_one]
            new_dic = {}
        new_3_dic[k] = new_new_dic

        new_new_dic = {}
    end_xcycyyy = {}
    end_xcycyyy['产品类型'] = new_3_dic

    table = tables[1]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)
    new_3_dic = {}
    thing_name = []
    new_dic = {}
    new_new_dic = {}

    for key, value in dict_list[0].items():
        if '产品类型' not in key:
            name = key
            thing_name.append(name)
    end_list = []
    end_list.append(dict_list[0])
    end_list.append(dict_list[1])

    for ddd in thing_name:
        for i in range(0, len(end_list)):
            key = end_list[i]['产品类型.1']
            value = end_list[i][f'{ddd}']
            new_dic[key] = value_new
        new_new_dic['规格'] = [new_dic]
        new_3_dic[ddd] = new_new_dic
        new_new_dic = {}
        new_dic = {}

    Installation_dimensions_url = {}
    Installation_dimensions_url['产品类型'] = new_3_dic

    product_name = 'MT60系列真彩触摸屏'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': end_xcycyyy, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_HIMI.append(end_dict_end)
    # with open(f'HMI人机界面.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get4_HIMI(url):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features_end = ''.join([item.strip() for item in Product_Features if item.strip()])

    # 2
    picture_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[2]/img/@src')[0]
    picture_url = urljoin(url_based, picture_url)
    Installation_dimensions_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions_url)
    product_name = 'MT90系列真彩触摸屏'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': picture_url, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_HIMI.append(end_dict_end)
    # with open(f'HMI人机界面.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


# PLC一体机
def get1(url):
    resp = re_txt(url)

    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/span/p[1]/span/strong/a/@href')[0]

    Product_Features_imgs = tree.xpath('//div[@class="Prod_xq_t2_list"]//samp[1]//p/span/img/@src')

    one_url = []
    for Product_Features_img in Product_Features_imgs:
        Product_Features_img = urljoin(url_based, Product_Features_img)
        one_url.append(Product_Features_img)
    Product_Features_img = ','.join(one_url)

    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features + '产品特点图：' + Product_Features_img
    # 3
    Installation_dimensions = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[3]/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions)

    # 2
    pictures_urls_buy_1 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]//td/a/@href')
    pictures_urls_buy_2 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/@href')
    pictures_urls_1 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]/td/a/img/@src')
    pictures_urls_2 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/img/@src')

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)

    def extract_key_value_pairs(my_dict):
        new_dict = {}
        end_dict = {}
        again_dict = {}
        found = False
        for key, value in my_dict.items():
            if key == value:
                if new_dict != {}:
                    end_dict[repeat_key] = new_dict
                    repeat_key = key
                    new_dict = {}
                else:
                    repeat_key = key
                    found = True
            elif found:
                new_dict[key] = value
            else:
                again_dict[key] = value
        end_dict['备注'] = value
        a = {**again_dict, **end_dict}
        return a

    def end_extract(list):
        aaa = {}
        kk = {}
        for i in range(1, len(list[0])):  # 1,5
            for k in range(1, len(list)):  # 0,len
                key = list[k]['0']
                value = list[k][f'{i}']
                aaa[key] = value
            oo = extract_key_value_pairs(aaa)
            key = list[0][f'{i}']
            kk[key] = oo
        return kk

    dict_list = end_extract(dict_list)
    dict_list_end = {}
    dict_list_end['产品类型'] = dict_list
    product_name = 'EX3G-C系列触摸屏PLC一体机'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': dict_list_end, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC.append(end_dict_end)
    # with open(f'PLC一体机.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


# formatted_dict = json.dumps(end_dict, indent=4,ensure_ascii=False)
def get2(url):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]/p[2]/span/strong/a/@href')[0]
    Product_Features_img = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[43]/img/@src')[0]
    Product_Features_img = urljoin(url_based, Product_Features_img)
    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features + '产品特点图：' + Product_Features_img
    # 3
    Installation_dimensions = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[3]/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions)

    # 2
    pictures_urls_buy_1 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]//td/a/@href')
    pictures_urls_buy_2 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/@href')
    pictures_urls_1 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]/td/a/img/@src')
    pictures_urls_2 = tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/img/@src')

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[1]
    json_data = table.to_json(orient="records", force_ascii=False)
    data_list = json.loads(json_data)

    # 插图
    i = 0
    for key, value in data_list[0].items():
        if value == None:
            data_list[0][key] = pictures_urls_1[i]
            i += 1
    i = 0
    for key, value in data_list[1].items():
        if value == None:
            data_list[1][key] = pictures_urls_2[i]
            i += 1
    data_list[0]['产品类型'] = '产品正面图片'
    data_list[1]['产品类型'] = '产品背面图片'

    def extract_key_value_pairs(my_dict):
        new_dict = {}
        end_dict = {}
        again_dict = {}
        found = False
        for key, value in my_dict.items():
            if key == value:
                if new_dict != {}:
                    end_dict[repeat_key] = new_dict
                    repeat_key = key
                    new_dict = {}
                else:
                    repeat_key = key
                    found = True
            elif found:
                new_dict[key] = value
            else:
                again_dict[key] = value
        end_dict['备注'] = value
        a = {**again_dict, **end_dict}
        return a

    new_dic = {}
    end_duc = {}
    title_first = list(data_list[0].keys())

    for k in range(1, len(title_first)):
        for i in range(0, len(data_list)):
            key = data_list[i]['产品类型']
            value_name = title_first[k]
            value = data_list[i][value_name]
            new_dic[key] = value
        end_dic = extract_key_value_pairs(new_dic)
        end_duc[value_name] = end_dic

    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    end_dicc = {}
    end_dicc['产品类型'] = end_duc
    product_name = 'EX3G-H系列触摸屏PLC一体机'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': end_dicc, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC.append(end_dict_end)
    # with open(f'PLC一体机.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get3(url):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features_end = ''.join([item.strip() for item in Product_Features if item.strip()])
    # 3
    Installation_dimensions = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[3]/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions)

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)

    def extract_key_value_pairs(my_dict):
        new_dict = {}
        end_dict = {}
        again_dict = {}
        found = False
        for key, value in my_dict.items():
            if key == value:
                if new_dict != {}:
                    end_dict[repeat_key] = new_dict
                    repeat_key = key
                    new_dict = {}
                else:
                    repeat_key = key
                    found = True
            elif found:
                new_dict[key] = value
            else:
                again_dict[key] = value
        end_dict['备注'] = value
        a = {**again_dict, **end_dict}
        return a

    def end_extract(list):
        aaa = {}
        kk = {}
        for i in range(1, len(list[0])):  # 1,5
            for k in range(1, len(list)):  # 0,len
                key = list[k]['0']
                value = list[k][f'{i}']
                aaa[key] = value
            oo = extract_key_value_pairs(aaa)
            key = list[0][f'{i}']
            kk[key] = oo
        return kk

    dict_list = end_extract(dict_list)
    dict_list_end = {}
    dict_list_end['产品类型'] = dict_list
    product_name = 'QM3G系列PLC一体机（渠道）'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': dict_list_end, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC.append(end_dict_end)
    # with open(f'PLC一体机.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


# PLC控制器
def get_data(url, product_name):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    # 产品图片
    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[1]//strong/a/@href')[0]

    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features
    # 3
    Installation_dimensions = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p[2]/span/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions)
    Install_text = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p[1]//text()')
    Install_text = ''.join([item.replace('\xa0', '').strip() for item in Install_text if item.strip()])
    Installation_dimensions_url = Install_text + '。' + Installation_dimensions_url

    # 2
    # pictures_urls_buy_1=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]//td/a/@href')
    # pictures_urls_buy_2=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/@href')
    # pictures_urls_1=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]/td/a/img/@src')
    # pictures_urls_2=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/img/@src')
    #
    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)

    new_dic = {}
    again_dic = {}
    fature = True
    new2_dic = {}
    key_sign = ''
    for i in range(0, len(dict_list)):
        y_n = dict_list[i]['0']
        if y_n is not None and i != 0:
            if key_sign:
                new2_dic[key_sign] = new_dic
                new_dic = {}
                key_sign = y_n  # 标志
                key = dict_list[i]['1']
                value = dict_list[i]['2']
                new_dic[key] = value
            else:
                fature = False
                key_sign = y_n  # 标志
                key = dict_list[i]['1']
                value = dict_list[i]['2']
                new_dic[key] = value
        elif fature:
            key = dict_list[i]['1']
            value = dict_list[i]['2']
            again_dic[key] = value
        else:
            key = dict_list[i]['1']
            value = dict_list[i]['2']
            new_dic[key] = value
    end_di = {**again_dic, **new2_dic, **new_dic}
    end_dic = {}
    end_dic['硬件结构'] = end_di

    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': end_dic, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC_K.append(end_dict_end)
    # with open(f'PLC控制器.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get_data_15(url, product_name):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    # 产品图片
    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # print(Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[2]/b/strong/a/@href')[0]
    Product_Features_img = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/img/@src')[0]

    Product_Features_img = urljoin(url_based, Product_Features_img)
    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features + '产品特点图：' + Product_Features_img
    # print(Product_Features_end)
    # 3

    Installation_dimensions_url = '无'
    # print(Installation_dimensions_url)

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[1]
    json_data = table.to_json(orient="records", force_ascii=False)
    data_list = json.loads(json_data)

    pictures_urls = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[2]/table[1]/tbody/tr[2]/td/a/img/@src')
    data_list[0]["CX3G- 16M"] = pictures_urls[0]
    data_list[0]["CX3G-24M"] = pictures_urls[1]
    data_list[0]["CX3G-32M"] = pictures_urls[1]
    data_list[0]["CX3G-48M"] = pictures_urls[2]
    data_list[0]["CX3G-34M"] = pictures_urls[2]
    data_list[0]["CX3G-64M"] = pictures_urls[3]
    data_list[0]["CX3G-80M"] = pictures_urls[3]

    def extract_key_value_pairs(my_dict):
        new_dict = {}
        end_dict = {}
        again_dict = {}
        found = False
        for key, value in my_dict.items():
            if key == value:
                if new_dict != {}:
                    end_dict[repeat_key] = new_dict
                    repeat_key = key
                    new_dict = {}
                else:
                    repeat_key = key
                    found = True
            elif found:
                new_dict[key] = value
            else:
                again_dict[key] = value
        end_dict['备注'] = value
        a = {**again_dict, **end_dict}
        return a

    new_dic = {}
    end_duc = {}
    title_first = list(data_list[0].keys())

    for k in range(1, len(title_first)):
        for i in range(0, len(data_list)):
            key = data_list[i]['产品类型']
            value_name = title_first[k]
            value = data_list[i][value_name]
            new_dic[key] = value
        end_dic = extract_key_value_pairs(new_dic)
        end_duc[value_name] = end_dic

    end_dicc = {}
    end_dicc['产品类型'] = end_duc

    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': end_dicc, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC_K.append(end_dict_end)
    # with open(f'PLC控制器.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)
    #
    # print(end_dict)


def get_data_9(url, product_name):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    # 产品图片
    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[1]//strong/a/@href')[0]

    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features
    # 3
    Installation_dimensions = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p[2]/span/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions)
    Install_text = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]/p[1]//text()')
    Install_text = ''.join([item.replace('\xa0', '').strip() for item in Install_text if item.strip()])
    Installation_dimensions_url = Install_text + '。' + Installation_dimensions_url

    tables = pd.read_html(url, encoding='utf-8')
    table = tables[0]
    json_data = table.to_json(orient="records", force_ascii=False)
    dict_list = json.loads(json_data)

    new_dic = {}
    again_dic = {'产品型号': 'CX3G-16MT'}
    fature = True
    new2_dic = {}
    key_sign = ''
    for i in range(0, len(dict_list)):
        y_n = dict_list[i]['0']
        if y_n is not None and i != 0:
            if key_sign:
                new2_dic[key_sign] = new_dic
                new_dic = {}
                key_sign = y_n  # 标志
                key = dict_list[i]['1']
                value = dict_list[i]['2']
                new_dic[key] = value
            else:
                fature = False
                key_sign = y_n  # 标志
                key = dict_list[i]['1']
                value = dict_list[i]['2']
                new_dic[key] = value
        elif fature:
            key = dict_list[i]['1']
            value = dict_list[i]['2']
            again_dic[key] = value
        else:
            key = dict_list[i]['1']
            value = dict_list[i]['2']
            new_dic[key] = value

    end_di = {**again_dic, **new2_dic, **new_dic}
    end_dic = {}
    end_dic['硬件结构'] = end_di
    end_dict_end = {product_name: end_dic}

    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': end_dict_end, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC_K.append(end_dict_end)
    # with open(f'PLC控制器.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get_L02(url):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    # 产品图片
    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)
    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features_end = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//p[1]/span/strong//a/@href')[0]
    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features_end
    # 3
    Installation_dimensions = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[3]/img/@src')[0]
    Installation_dimensions_url = urljoin(url_based, Installation_dimensions)

    # 2
    dict_list = tree.xpath("//*[@id='tabs_pro']/div[2]/samp[2]/img/@src")[0]
    dict_list = urljoin(url_based, dict_list)
    product_name = 'L02系列PLC控制器'
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': dict_list, "安装尺寸": Installation_dimensions_url}
    end_dict_end = {product_name: end_dict}

    end_list_json_PLC_K.append(end_dict_end)
    # with open(f'PLC控制器.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False, indent=4)


def get_data_PLC(url, product_name):
    resp = re_txt(url)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)

    # 产品图片
    Product_img = tree.xpath('//div[@class="Prod_xq_t1_left"]/img/@src')[0]
    Product_img = urljoin(url_based, Product_img)

    # 1
    Product_Features = tree.xpath('//div[@class="Prod_xq_t2_list"]/samp[1]//text()')
    Product_Features = ''.join([item.replace('\xa0', '').strip() for item in Product_Features if item.strip()])
    buy_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[1]/p[1]/span/strong/a/@href')[0]

    Product_Features_end = '购买链接：' + buy_url + '。' + Product_Features

    # 3

    Installation_dimensions_url = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[3]//text()')
    Installation_dimensions_url = ''.join(
        [item.replace('\xa0', '').strip() for item in Installation_dimensions_url if item.strip()])

    # 2
    # pictures_urls_buy_1=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]//td/a/@href')
    # pictures_urls_buy_2=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/@href')
    # pictures_urls_1=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[2]/td/a/img/@src')
    # pictures_urls_2=tree.xpath(f'//div[@class="Prod_xq_t2_list"]/samp[2]/table/tbody/tr[3]/td/a/img/@src')
    #

    dict_list = tree.xpath('//*[@id="tabs_pro"]/div[2]/samp[2]/img/@src')[0]
    dict_list = urljoin(url_based, dict_list)
    end_dict = {'产品名称': product_name, '产品图片': Product_img, '产品特点': Product_Features_end,
                '产品参数': dict_list, "安装尺寸": Installation_dimensions_url}

    end_dict_end = {product_name: end_dict}
    print(end_dict_end)
    end_list_json_PLC_K.append(end_dict_end)
    # with open(f'PLC控制器.json', 'a+', encoding='utf-8') as f:
    #     json.dump(end_dict_end, f, ensure_ascii=False,indent=4)


def HIMI_re_json():
    get1_HIMI('http://www.coolmay.com/ProductDetail.aspx?ColumnId=98&ArticleId=2322&Language=34&Terminal=41')
    print("完成TK系列触摸屏人机界面（渠道）")
    get2_HIMI('http://www.coolmay.com/ProductDetail.aspx?ColumnId=98&ArticleId=2323&Language=34&Terminal=41')
    print("完成TP系列触摸屏人机界面")
    get3_HIMI('http://www.coolmay.com/ProductDetail.aspx?ColumnId=98&ArticleId=653&Language=34&Terminal=41')
    print("完成MT60系列真彩触摸屏")
    get4_HIMI('http://www.coolmay.com/ProductDetail.aspx?ColumnId=98&ArticleId=2426&Language=34&Terminal=41')
    print("完成MT90系列真彩触摸屏")

    with open(f'HMI人机界面.json', 'w', encoding='utf-8') as f:
        json.dump(end_list_json_HIMI, f, ensure_ascii=False, indent=4)
    print("HIMI人机界面所有任务完成，请等待下次任务")

def PLC_YTJ_json():
    get1('http://www.coolmay.com/ProductDetail.aspx?ColumnId=94&ArticleId=2324&Language=34&Terminal=41')
    print("完成EX3G-C系列触摸屏PLC一体机")
    get2('http://www.coolmay.com/ProductDetail.aspx?ColumnId=94&ArticleId=1100&Language=34&Terminal=41')
    print("完成EX3G-H系列触摸屏PLC一体机")
    get3('http://www.coolmay.com/ProductDetail.aspx?ColumnId=128&ArticleId=2321&Language=34&Terminal=41')
    print("完成QM3G系列PLC一体机（渠道）")
    with open(f'PLC一体机.json', 'w', encoding='utf-8') as f:
        json.dump(end_list_json_PLC, f, ensure_ascii=False, indent=4)
    print("PLC一体机全部任务完成,请等待下次任务")

def PLC_KZQ_json():
    resp = re_txt(url='http://www.coolmay.com/PicList.aspx?ColumnId=206&Language=34&Terminal=41')
    resp.encoding = 'utf-8'

    tree = etree.HTML(resp.text)

    url_more = []
    name_more = []
    while tree.xpath('//*[@id="Pager1"]/a[4]/@href') != []:
        url_2 = tree.xpath('//*[@id="Pager1"]/a[4]/@href')[0]
        url_2 = urljoin(url_based, url_2)
        resp_more = re_txt(url=url_2)
        tree = etree.HTML(resp_more.text)
        url_more = tree.xpath('//ul[@class="wrapfix"]/li/div[1]/a/@href')
        url_more = [urljoin(url_based, item) for item in url_more]
        name_more = tree.xpath('//ul[@class="wrapfix"]/li/div[2]/a/text()')
        name_more = [item.replace('\xa0', '').strip() for item in name_more if item.strip()]

    tree = etree.HTML(resp.text)
    urls = tree.xpath('//ul[@class="wrapfix"]/li/div[1]/a/@href')
    urls = [urljoin(url_based, item) for item in urls] + url_more

    product_names = tree.xpath('//ul[@class="wrapfix"]/li/div[2]/a/text()')
    product_names = [item.replace('\xa0', '').strip() for item in product_names if item.strip()] + name_more

    for i in range(0, len(urls)):
        if i == 8:
            get_data_9(urls[i], product_names[i])
        elif i == 14:
            get_data_15(urls[i], product_names[i])
        else:
            get_data(urls[i], product_names[i])

        print(f"GX3G完成第{i + 1}项")
    print(" CX3G PLC控制器完成")

    get_L02('http://www.coolmay.com/ProductDetail.aspx?ColumnId=209&ArticleId=2325&Language=34&Terminal=41')
    print("L02 PLC控制器完成")
    get_data_PLC('http://www.coolmay.com/ProductDetail.aspx?ColumnId=211&ArticleId=2486&Language=34&Terminal=41',
                 '顾美薄型PLC控制器 卡片式设计 FX3GC-16M FX3GC-32M')
    print("FX3GC PLC控制器（顾美薄款）完成")

    with open(f'PLC控制器.json', 'w', encoding='utf-8') as f:
        json.dump(end_list_json_PLC_K, f, ensure_ascii=False, indent=4)

    print("PLC控制器所有任务完成")

if __name__ == '__main__':
    # HIMI人机界面
    HIMI_re_json()
    # PLC一体机
    PLC_YTJ_json()
    # PLC控制器
    PLC_KZQ_json()
    print("程序执行完毕")

