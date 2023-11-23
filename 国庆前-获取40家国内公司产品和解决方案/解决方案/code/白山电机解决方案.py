import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    url = 'https://www.bsjd.com/case-item-23.html'
    title = '步进电机一般工作场合的应用(DM365MA)'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'这个视频是脚手架焊接设备，步进电机在设备上需要在DC48V以内，6牛米以上电机需要工作在480转/分钟左右。负载相对较重。客户因为考虑设备生产期间需24小时以上长时间连续运行。所以选用的是三相步进马达及适配的直流驱动器。',
            'type':'text'
        },{
            'content':['https://img01.71360.com/file/read/www/M00/FF/86/wKj0iWHJMJqAU94fABIJE-zCB74768.mp4',
                       'https://img01.71360.com/file/read/www/M00/FF/86/wKj0iWHJMKaAZzq6ABaEb8lJf40881.mp4'],
            'type':'movie'
        },
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取方案{len(final_dic["pro"])}/3条数据')

    url = 'https://www.bsjd.com/case-item-22.html'
    title = '真空环境下使用步进电机'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'这里的真空环境并不是绝对意义上的真空环境，只是相对的。真空环境下由于无外部大气压，电机会出现渗油现象，污染工作对象。电机发热量无法通过空气传导进行有效散热，电机长时间工作，电机会随时间累积过度发热出现烧毁线路的现象。下面这个设备是电机在真空涂板设备上的应用。',
            'type':'text'
        },{
            'content':['https://img01.71360.com/file/read/www/M00/FF/85/wKj0iWHJMByActLOAAFw3RDdcXk494.jpg',
                       'https://img01.71360.com/file/read/www/M00/FF/85/wKj0iWHJMCCAQGa3AAH2NWSpsKQ035.jpg',],
            'type':'img'
        },
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取方案{len(final_dic["pro"])}/3条数据')

    url = 'https://www.bsjd.com/case-item-21.html'
    title = '步进电机超高速运行案例示范(D2HB44M)'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'步进电机由于电机自身特性，存在输出力矩随运行转速的提升而出现力矩下滑的现象。所以，步进电机一般工作场合应用转速都在300转/分钟~600转/分钟。特殊场合通过提升驱动器工作电压可以工作到900转/分钟以上，再高的运行速度，客户一般都会经人介绍使用伺服。这个运行视频是步进电机在DC24V供电电源供电，因为负载很轻，凭借对机械结构的优良设计，步进电机最高实际使用运行速度3000转/分钟以上。设备生产效率上和大部分使用伺服装备的同款设备一致。视频中该设备最低运行速度要求为1200转/分钟。',
            'type':'text'
        },{
            'content':['https://img01.71360.com/file/read/www/M00/FE/83/wKj0iWHGg-2AfS86ACtYoYE7kg0953.mp4',
                       'https://img01.71360.com/file/read/www/M00/00/69/wKj0iWHJrbuANkTJAC2Nsnnt6YE152.mp4',],
            'type':'movie'
        },
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取方案{len(final_dic["pro"])}/3条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'白山电机解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')