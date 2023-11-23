import json
import requests
from lxml import etree
from html import unescape
from loguru import logger
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


@logger.catch
def parse_solu():
    final_dic = {'pro':[]}
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
        'Cookie':'kndctr_8EB3430663583A300A495E9C_AdobeOrg_identity=CiY1MTQwOTkwODQxMTI0NDY4MzkyMzUzNTgzNjMyMzA3MzgyMzIwNlIRCMzJj_K6MRgBKgRKUE4zMAHwAczJj_K6MQ==; kndctr_8EB3430663583A300A495E9C_AdobeOrg_cluster=jpn3; AMCV_8EB3430663583A300A495E9C%40AdobeOrg=MCMID|51409908411244683923535836323073823206; AWSALB=HtzHufGWGvQtGqGxAUe8a5m5A6wG1zk9QzjgZnxwSdnKqs1WZa2W/w5Rac1j9S31J49x6kxnKSK+U4nBF0ITYQQK9MIRw62Phf33pizn7Y1K10BFciWsNctnKRZB; AWSALBCORS=HtzHufGWGvQtGqGxAUe8a5m5A6wG1zk9QzjgZnxwSdnKqs1WZa2W/w5Rac1j9S31J49x6kxnKSK+U4nBF0ITYQQK9MIRw62Phf33pizn7Y1K10BFciWsNctnKRZB',
        'Referer':'https://www.hiconics.com/cn/solution',
    }
    title = '户用储能解决方案'
    ProductUrl,Description = [],[]
    solu_url = 'https://www.hiconics.com/cn/solution/solution-detail?articleId=100264&channelArticleId=100530&language=zh&resouceCode=hiconics%20solution'
    firstTypeName,secondTypeName = '',''
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    desp_text = '多种用电方案——绿色低碳、经济用电、供能保障'
    Description.append({'content':desp_text,'type':'text'})
    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = secondTypeName
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = unescape(resp.text.strip())
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    final_dic['pro'].append(solu_dic)

    title = '户用分布式光伏EPC'
    ProductUrl,Description = [],[]
    solu_url = 'https://www.hiconics.com/cn/solution/solution-detail?articleId=100277&channelArticleId=100529&language=zh&resouceCode=hiconics%20solution'
    firstTypeName,secondTypeName = '',''
    resp = requests.get(url=solu_url,headers=headers)
    resp.encoding = 'utf-8'
    desp_text = '阳光房电站阳光房电站人字坡造型设计不仅达到了发电的目的，还为用户额外增加了屋顶可用空间，电站具备防雨功能用户可以在电站下休闲娱乐，电站可以有效防晒，使室内温度降低3~5度。双坡电站对比阵列式双坡式增加了电站的发电量，规整的外观设计让屋顶焕然一新，更美观，对原有的屋顶起到了很好的保护作用阵列式电站结合屋顶原有设计提供了顺屋面安装的U钢锌铝镁支架形式，基座稳定，不影响原有的排水，对屋顶也起到了更好的保护作用。庭院式电站大大增加了电站的发电量，用户收益更多，同时用户可在庭院电站下休闲、储藏物品，增加了用户的庭院可利用空间，外形美观，耐磨防腐。合康户用分布式光伏解决方案集光伏电站开发、设计、建设、智能运维和专业咨询服务为一体的全流程资产开发建设运营平台，主要运营分布式户用光伏相关业务，整合资金、供应链、数字化系统、技术研发、仓配网络优势，发挥运营效率。致力成为全球领先的新能源领域产品提供商'
    Description.append({'content':desp_text,'type':'text'})
    solu_dic = {}
    solu_dic['FirstType'] = firstTypeName
    solu_dic['SecondType'] = secondTypeName
    solu_dic['SolutionUrl'] = solu_url
    solu_dic['SolutionHTML'] = unescape(resp.text.strip())
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = ProductUrl
    final_dic['pro'].append(solu_dic)

    return final_dic


if __name__ == "__main__":
    logger.add('runtime.log',retention='1 day')

    final_dic = parse_solu()
    filename,dic = f'合康新能解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')