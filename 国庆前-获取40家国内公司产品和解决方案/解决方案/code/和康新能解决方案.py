import json
import requests
from loguru import logger


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    url = 'https://www.hiconics.com/cn/solution/solution-detail?articleId=100277&channelArticleId=100529&language=zh&resouceCode=hiconics%20solution'
    resp = requests.get(url=url,headers=headers)
    title = '户用分布式光伏EPC'
    Description = {
        '阳光房电站':[{
            'content':'阳光房电站人字坡造型设计不仅达到了发电的目的，还为用户额外增加了屋顶可用空间，电站具备防雨功能用户可以在电站下休闲娱乐，电站可以有效翻晒，使市内温度降低3~5度。',
            'type':'text'
        },{
            'content':[
                'https://iscrm-oss-hk.midea.com/article-mgmt/35ee0404-7417-4ffb-9bc7-3cc0de1198f3',
                'https://iscrm-oss-hk.midea.com/article-mgmt/11cb799a-82eb-4518-91f6-242be9786465',
                'https://iscrm-oss-hk.midea.com/article-mgmt/1df74d4b-bc88-4895-a60f-1992c53ac130'
            ],
            'type':'img'
        }
        ],
        '双坡电站':[{
            'content':'对比阵列式双坡式增加了电站的发电量，规整的外观设计让屋顶焕然一新，更美观，对原有的屋顶起到了很好的保护作用。',
            'type':'text'
        },{
            'content':[
                'https://iscrm-oss-hk.midea.com/article-mgmt/bbb04f48-fab4-47ee-a529-d9aefd00c18b',
                'https://iscrm-oss-hk.midea.com/article-mgmt/e68fa8e9-8575-4d44-af6e-d9f95f9740b3',
            ],
            'type':'img'
        }
        ],
        '阵列式电站':[{
            'content':'结合屋顶原有设计提供了顺屋面安装的U钢锌铝镁支架形式，基座稳定，不影响原有的排水，对屋顶也起到了更好的保护作用。',
            'type':'text'
        },{
            'content':[
                'https://iscrm-oss-hk.midea.com/article-mgmt/ba4d5ad6-e58b-4f4c-b91d-de8d688f9efb',
            ],
            'type':'img'
        }
        ],
        '庭院式电站':[{
            'content':'大大增加了电站的发电量，用户收益更多，同时用户可在庭院电站下休闲、储藏物品，增加了用户的庭院可利用空间，外形美观，耐磨防腐。合康户用分布式光伏解决方案集光伏电站开发、设计、建设、智能运维和专业咨询服务为一体的全流程资产开发建设运营平台，主要运营分布式户用光伏相关业务，整合资金、供应链、数字化系统、技术研发、仓配网络优势，发挥运营效率。致力成为全球领先的新能源领域产品提供商',
            'type':'text'
        },{
            'content':[
                'https://iscrm-oss-hk.midea.com/article-mgmt/66a2db22-e1ef-4d9c-9ee0-2beae0722ae5',
                'https://iscrm-oss-hk.midea.com/article-mgmt/6dc37d39-b134-464e-a486-1ff88665596b',
            ],
            'type':'img'
        }
        ]
    }
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)

    url = 'https://www.hiconics.com/cn/solution/solution-detail?articleId=100264&channelArticleId=100530&language=zh&resouceCode=hiconics%20solution'
    resp = requests.get(url=url,headers=headers)
    title = '户用储能解决方案'
    Description = {
        '多种用电方案':[
        {
            'content':[
                'https://iscrm-oss-hk.midea.com/article-mgmt/23561cc9-511c-4414-82ce-1473d2e06691',
                'https://iscrm-oss-hk.midea.com/article-mgmt/3da1f083-8db6-416a-94b8-d8f3a2aee685',
                'https://iscrm-oss-hk.midea.com/article-mgmt/9df50408-9977-4ebd-bc51-9bb18e69a429',
                'https://iscrm-oss-hk.midea.com/article-mgmt/ffd80a67-c82d-40a3-8226-23c541598281',
                'https://iscrm-oss-hk.midea.com/article-mgmt/70543326-335a-48ff-9bc0-d8b16ae056a9',
            ],
            'type':'img'
        }
        ]
    }
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }
    final_dic = get_solution(headers)
    filename,dic = f'和康新能解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')