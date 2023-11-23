import json
import requests
from loguru import logger


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    FirstType = '移动机器人行业'
    pro_url = 'https://www.hkt-robot.com/pages/info.aspx?fid=3&sid=13&nid=37'
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    title = '视觉定位机'
    Description = {
        'content':'https://vali-ugc.cp31.ott.cibntv.net/6776191A6014171CC564964AF/03000A01005F17EF16724115AD43397A6AC1EB-6FD4-494B-95F6-3A89852374C5.mp4?ccode=0512&duration=19&expire=18000&psid=4b52467478bde490d91093e10e9f219741346&ups_client_netip=2470079a&ups_ts=1696986526&ups_userid=&utid=ElhzHUG%2FWHUCASRwB54YHLpy&vid=XNDc2MjYxOTI0MA%3D%3D&vkey=B75420ec65fa912e5cce23b5251a79649&eo=0&t=9996ebb0e358926&cug=1&fms=48436fb339937b92&tr=19&le=12fa302e22c730ce4aca471cf43a4503&ckt=1&m_onoff=0&rid=200000003194B749DD3D489F5C2B491C7A3DEBBA02000000&type=mp4sd&bc=2&dre=u145&si=611&dst=1&app_ver=1.10.1.1',
        'type':'movie'
    }
    solu_dic = {}
    solu_dic['FirstType'] = FirstType
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = pro_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取方案{len(final_dic["pro"])}/条数据')
    
    FirstType = '移动机器人行业'
    pro_url = 'https://www.hkt-robot.com/pages/info.aspx?fid=3&sid=13&nid=36'
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    title = '动静切换定位机一机双定'
    Description = {
        'content':'https://v2v283407gdcqp432a6zz31s5dxyvpr9u.mobgslb.tbcache.com/youku/6773e424c4b4b721443cb6439/0300080100646DCA7F5BDCD4EAFC3ECCACB87E-34CB-4C6C-98EE-D28700971A71.mp4?sid=169698684900010002602_00_Bb39b019ab805c36862d9df1caecb62db&sign=51c66e95f1889622cfa29970bfa91aae&ctype=50&ali_redirect_domain=vali.cp31.ott.cibntv.net&ali_redirect_ex_ftag=c938bb40e91bfda11b02237d9199e4f7edf851b7bf681add&ali_redirect_ex_tmining_ts=1696986848&ali_redirect_ex_tmining_expire=3600&ali_redirect_ex_hot=100',
        'type':'movie'
    }
    solu_dic = {}
    solu_dic['FirstType'] = FirstType
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = pro_url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = title
    solu_dic[title] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取方案{len(final_dic["pro"])}/条数据')
    
    FirstType = '半导体行业'
    pro_url = 'https://www.hkt-robot.com/pages/info.aspx?fid=3&sid=13&nid=35'
    resp = requests.get(url=pro_url,headers=headers)
    resp.encoding = 'utf-8'
    title = 'HT系列伺服电机 200w'
    Description = {
        'content':'https://v2vuub89pe163nquvej98279rntrxy9s8.mobgslb.tbcache.com/youku/65729818c094571e91bb62086/0300080100646DCA7F5BDCD4EAFC3ECCACB87E-34CB-4C6C-98EE-D28700971A71.mp4?sid=169698695400010003349_00_Ba099f89e69f5040433e0e8ff8c959f4e&sign=0c1abd3717aea0a055b8893700b20624&ctype=50&ali_redirect_domain=vali.cp31.ott.cibntv.net&ali_redirect_ex_ftag=ef0a734131a24ae2456bbcb9030cad09cfd795d83ecb3a21&ali_redirect_ex_tmining_ts=1696986954&ali_redirect_ex_tmining_expire=3600&ali_redirect_ex_hot=100',
        'type':'movie'
    }
    solu_dic = {}
    solu_dic['FirstType'] = FirstType
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = pro_url
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
    filename,dic = f'恒科通机器人解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')