import json
import requests
from loguru import logger


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    url = 'https://www.fujielectric.com.cn/show-314.html'
    title = '电力可视化解决方案'
    resp = requests.get(url=url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'问题点: 伴随着电力系统规模的不断扩大，电网运行方式对信息刷选和数据计算的工作量逐年增加。传统的电力管理已不在适用。将电力管理方式规范化，标准化，自动化，能在很大程度上减轻工作人员的负担，并提高计算结果的准确性。',
            'type':'text'
        },{
            'content':'解决方法: EMS（能源管理系统）是通过控制和管理实现节能的重要工具。     这次介绍的是使用投资少效果好的EMS产品（GreenTerminal）的节能。',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201810/52.png',
            'type':'img'
        },{
            'content':'特性',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201810/55.png',
            'type':'img'
        },{
            'content':'可视化构成（例）',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201810/59.png',
            'type':'img'
        },{
            'content':'检测器械连接构成 ',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201810/61.png',
            'type':'img'
        },{
            'content':'监视功能的扩张，应用',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201810/63.png',
            'type':'img'
        },{
            'content':'能源利用的优化',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201810/66.png',
            'type':'img'
        }
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/5条数据')

    url = 'https://www.fujielectric.com.cn/show-293.html'
    title = '隧道除尘解决方案'
    resp = requests.get(url=url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'消除公路隧道污染物。提高公路隧道能见度。富士电机的交流式静电除尘器能够解决普通静电除尘器一直存在的二次扬尘问题。',
            'type':'text'
        },{
            'content':['https://www.fujielectric.com.cn/uploadfiles/image/201606/362.jpg'],
            'type':'img'
        },{
            'content':'特性:收集的SPM是直流除尘器的两倍。防止二次扬尘。',
            'type':'text'
        },{
            'content':'结构:风机把公路隧道内被粉尘和烟尘污染的空气吸入静电除尘器，通过除尘器处理后，排出洁净的空气到大气中。导流板安装在空气通道的拐角，让清洁的空气顺畅地流进通道并通过消音器，直到从通风塔被排出。',
            'type':'text'
        },{
            'content':['https://www.fujielectric.com.cn/uploadfiles/image/201606/382.gif'],
            'type':'img'
        },{
            'content':'交流静电除尘器 (AC ESP):交流静电除尘器由除尘单元和机柜组成，每个机柜内装有数个包含预荷电部和收尘部的除尘单元。当处理风速达到9m/s时，除尘效率能达到90%，压力损失为200Pa。详情见附件目录。',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201606/384.jpg',
            'type':'img'
        },{
            'content':'高压交流电源:高压交流电源能产生静电除尘器的预荷电部和收尘部所需的高电压，这是为交流静电除尘器特别开发的装置。详情见附件目录。',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201606/385.jpg',
            'type':'img'
        },{
            'content':'污染空气通过风机，从隧道侧壁上的吸风口被吸入旁路式隧道内除尘器里，经过处理后，再把干净的空气通过旁路隧道的另一端送回公路隧道内。',
            'type':'text'
        },{
            'content':'https://www.fujielectric.com.cn/uploadfiles/image/201606/394.gif',
            'type':'img'
        }
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/5条数据')

    url = 'https://www.fujielectric.com.cn/show-293.html'
    title = '隧道除尘解决方案'
    resp = requests.get(url=url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'需要解决问题:◆通过控制锅炉O2排气,使排气热损失减少，削减锅炉燃料费的节能方案已经实施。能否更大程度的削减燃料费用成为锅炉节能的一大课题。',
            'type':'text'
        },
        {
            'content':'解决方法:◆通过实施「超稀薄空气燃烧解决方案包装（专利申请中）」，与实施控制锅炉O2排气锅炉相比，更加能削减▲０．５－▲１．５％的燃料费用◆锅炉是将燃料和空气投入到炉内,使之燃烧而产生热能的装置。针对当时的燃料而投入的空气比率（空气比）过大的话,未燃烧空气会伴随着热能一起从烟筒被排放，成为热能损失（排气热能损失）。相反，如果空气比率过小的话,由于不完全燃烧会产生的CO，同样也会产生热损失。产生热能损失的话,如同生产蒸气一样需要相应的锅炉燃料（燃料费）会增加。◆通常根据锅炉排气O2控制可以减少热损失（空气比率如下面的图中的领域），我们的方案，更加降低空气比率，正常运行时会产生微量的CO排气的超稀薄空气燃烧领域下（空气比率是下面图中的領域）进行控制操作。超稀薄空气燃烧解决方案具有以下的性能 ◆空气过剩会引起的锅炉排气热损耗，空气投入的不完全燃烧也会引起锅炉CO排气热损耗，我公司根据独自的燃烧计算方法求出最适合方案，根据控制使微量的CO排气连续产生，使锅炉总体热损耗降到最小，削减燃料费用。◆锅炉负荷发生变化时,控制空气过剩，防止从烟筒里产生黑烟。◆环保标准对CO排放标准有规定的情况下,优先于控制锅炉总体热损耗，可实施CO达标排放,控制。◆锅炉负荷突然发生变化的情况下,促使锅炉的CO排气值不超过上限值（可自由设定）而进行CO模块控制。',
            'type':'text'
        },
        {
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/407.png',
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/409.png'
            ],
            'type':'img'
        },
        {
            'content':'效果（例）:超稀释空气燃烧解决方案的导入效果表示。',
            'type':'text'
        },
        {
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/411.png',
            ],
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/5条数据')

    url = 'https://www.fujielectric.com.cn/show-292.html'
    title = 'PM2.5颗粒物成分分析仪器(实时在线监测仪)'
    resp = requests.get(url=url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'特点:实时监控，可同时检测分析PM2.5中，主要硫酸盐，硝酸盐和黑碳等粒径及数量，并每5至15分钟（根据颗粒物浓度，浓度越浓时间越短）。分析一次空气中颗粒物分布，实时掌握最新的环境污染成分动向。',
            'type':'text'
        },
        {
            'content':'主要规格:质量浓度范围：PM2.5: 0～1000μg/m?黑炭及各种成分盐： 0～300μg/m?设置场所：屋内规格设置环境：15～35℃、30～85%RH外观尺寸（WHD）：装置主机：640×1800×828mm主机外配件*1：750×560×520mm重量：装置主机：約300kg；主机外配件*1：約100kg电源?接地：单相220V、50Hz、D种接地电力消费：约1.3kVA (最大2.3kVA) （包含主机外配件的电力消费）',
            'type':'text'
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/5条数据')

    url = 'https://www.fujielectric.com.cn/show-1394.html'
    title = '富士电机除尘器产品'
    resp = requests.get(url=url,headers=headers,verify=False)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'产品线',
            'type':'text'
        },{
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/396.png',
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/397.png'
                ],
            'type':'img'
        },{
            'content':'产品原理及富士电机除尘器特征',
            'type':'text'
        },{
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/399.png'
                ],
            'type':'img'
        },{
            'content':'富士电机除尘器特征',
            'type':'text'
        },{
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/401.png'
                ],
            'type':'img'
        },{
            'content':'过往业绩',
            'type':'text'
        },{
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/402.png'
                ],
            'type':'img'
        },{
            'content':'峰会活动',
            'type':'text'
        },{
            'content':[
                'https://www.fujielectric.com.cn/uploadfiles/image/201606/403.png'
                ],
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/5条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'富士电机解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')