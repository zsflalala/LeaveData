import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}
    url = 'http://www.dayond.com/news_info_110.html'
    title = '大研工控低压直流伺服在智能仓储和物流行业的应用'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'一、背景现代仓储和物流的发展有两个明显的特点，一是智能化，仓储和物流管理系统能够与电商系统或产线系统无缝对接，二是自动化，用相应的机器替代人，能够满足高效、精准和低成本的需求。AGV（自动引导运输车）就是适应这种需求应运而生，快速成为智能仓储的刚需设备，并凭借良好的应用特性，也广泛地应用于汽车制造、家电产线、纺织生产、药品输送、造纸、烟草和电子制造等行业。在电商蓬勃发展的推动下，快递分拣已成为快速发展的领域，不管是一份四分拣，还是交叉带分拣，都呈现出高速增长的态势，将人从长时间繁琐的分拣作业中解放出来，也降低了快递公司的运营成本。二、AGV在智能仓储和物流行业的应用简介AGV在仓储和物流行业的价值首先体现在替代人工。国内现在的用工成本已经超过东南亚及周边国家，而且存在用工荒的问题，加之仓储和物流行业工作强度大，工作时间长，用机器替代人成为迫切需求。另一个现实的需求是仓储和物流需要对接前端和后端，物品转移的同时需要完成数据的转移。如此种种因素，推动AGV在仓储和物流行业得到了快速导入和普遍应用。AGV的运动控制结构主要有三种。第一种是普通的两轮差速结构，第二种是轮舵结构，第三种是电动车常用的轮毂结构。两轮差速结构主要通过对两个运动轴做速度差的方法实现转向；轮舵结构是AGV专用机械结构，机构上有专门的转向电机轴；轮毂结构的原理类似于差速结构，只是电机采用了轮毂电机。还有一种结构俗称“麦克纳姆轮”，AGV小车做成四轮全向移动的结构以适应特定应用场合。三、大研工控低压直流伺服在AGV的应用简介AGV的电机驱动控制系统传统采用直流无刷电机+行星减速机，该方案成本低，但存在控制精度低和可靠性不足的问题，很难满足AGV越来越高的要求，直流无刷电机被低压直流伺服电机取代已成主流。大研工控针对AGV的低压直流伺服方案有两种，一种是驱动器和电机独立的分体式伺服，适用差速、舵轮、麦克纳姆轮结构，将电机更替为轮毂电机，也适用于轮毂结构；另一种是驱动器内置于电机内部的一体化伺服，免除繁琐接线，简化维护。大研工控的低压直流伺服方案应用于AGV有如下特点：1、18～80V直流宽电压范围，适应AGV大范围快速移动对电源的移动需求，适应电池消耗的电压降低和电压波动。2、灵活的控制方式，驱动器可以通过脉冲、RS232、485、CAN、模拟量等方式对低压直流伺服进行控制，可根据AGV要求进行功能定制，也可适应上位机要求修改协议。3、低压直流伺服电机功率段100W~1500W，电机效率高，能耗小，可供客户根据AGV的结构要求自由选型搭配，还可根据应用要求进行定制开发，比如低速大扭矩直驱伺服电机。4、伺服系统具过载能力强，定位精度高，响应快，可靠耐用。大研工控的低压直流伺服已经成功应用于汽车制造、各类叉车、大型仓储和物流分拣等行业的AGV，完全满足AGV平稳、准确、可靠的应用要求，相较于国外的相同方案，性价比优势明显，相较于国内的类似方案，更加专业可靠。四、大研工控低压直流伺服在快递分拣的应用简介快递已经成为我们生活里不可或缺的一部分，大量的快件纯粹依靠人工分拣根本满足不了快递行业的要求，分拣设备因此应运而生。分拣设备早先采用交流电机或直流无刷电机加装减速机，后续封装外转子直流无刷电机和减速机的直流无刷滚筒逐渐成为主流。大研工控研究快递分拣应用现状，针对快递分拣的应用特性，专门开发了快递分拣专用的直流伺服驱动器和直流伺服滚筒，直流伺服驱动器可以通过485或IO控制，使用航空插头方便安装和维护，直流伺服滚筒摒弃了减速机采用了直驱的方式。直流伺服滚筒相较于直流无刷滚筒具有如下特点：1、响应快。直流无刷滚筒启停最短需要800毫秒，直流伺服滚筒启停只需要100毫秒，甚至更短，明显提升分拣效率。2、可精准走位。直流无刷滚筒只能跑速度模式，常规最低转速100多转，也可以通过软件实现大致走位，但负载不同可能都会造成走位不准。直流伺服滚筒不仅可以跑速度模式实现1转/分钟的转动，也可以通过高精编码器跑位置模式，实现精准走位。3、走得稳。直流无刷滚筒跑速度模式的特性决定了难以平稳启停，因此难以满足某些分拣应用要求，而直流伺服滚筒完全可以切换位置模式，并采用S形加减速平稳启停，避免快件损伤或甩落。4、耐用。直流无刷滚筒内置减速机，常规来说使用过程中机构都会磨损，而直流伺服滚筒采用直驱方式，省掉了减速机这个寿命瓶颈，提高了客户的投入产出比。5、过载能力强。直流伺服滚筒恒力矩，标准型号5N·m，可以三倍过载到15 N·m，从负载适应性上明显好于直流无刷滚筒。',
            'type':'text'
        },{
            'content':['http://www.dayond.com/upload/20210224/1614164992116874.jpg','http://www.dayond.com/upload/20210224/1614164992798411.jpg'],
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/2条数据')

    url = 'http://www.dayond.com/news_info_109.html'
    title = '大研工控低压直流伺服助力移动机器人井喷发展'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    Description = [
        {
            'content':'一、背景随着仓储物流的迅猛发展和中国制造2025的强力推进，移动机器人已经成为非常重要的有生力量，不仅能够实现物品的快速移动，而且承载着信息的流转，在仓储搬运、物流分拣、汽车产线、家电制造、智能巡检、药品配送、移动雷达、电子加工、互动娱乐等领域均被快速应用，可以预见，未来的一两年内就会迎来井喷发展，并将在广度和深度两方面持续增长。二、移动机器人伺服方案移动机器人目前较普遍的包括AGV、RGV（货架穿梭车）、分拣机器人、巡检车等等，以下仅就AGV的伺服方案做个简单介绍，AGV运动由以下三个部分完成：1、行走：负责机器人的前进、后退和转向，根据负载和惯量大小，低压直流伺服电机的功率100W-1.5KW不等。2、顶升：负责货架或者物品的上升和下降，根据负载大小，低压直流伺服电机的功率100W-750KW不等，电机一般需加装刹车。3、旋转：负责承载物品的旋转，根据负载大小，低压直流伺服电机的功率100W-400W不等。大研工控适应AGV的应用特点，推出驱动器内置于电机内部的一体化伺服，功率100W-750W，抗干扰性好，免除繁琐接线，简化维护保养。三、应用特点1、18-72V直流宽电压范围，AGV凭借自身电池即可自如工作。2、系统可通过脉冲、RS232、RS485、CAN等方式对伺服灵活集约控制。3、行走和旋转可根据AGV的要求自由选型搭配，电机效率高，节能环保。4、顶升伺服电机适应AGV狭小空间定制而成，停转刹车自锁，大扭力。5、伺服内置加减速，运动平滑，启停快速而平稳。6、过载能力强，定位精度高，响应快，可靠性高。',
            'type':'text'
        },{
            'content':['http://nfs.gongkong.com/Upload/editor/201708/20170811171815619_w.png',
                       'http://nfs.gongkong.com/Upload/editor/201708/20170811171816134_w.png',
                       'http://nfs.gongkong.com/Upload/editor/201708/20170811171950556_w.png',
                       'http://nfs.gongkong.com/Upload/editor/201708/20170811171951431_w.png',
                       'http://nfs.gongkong.com/Upload/editor/201708/20170811171936056_w.png',
                       'http://nfs.gongkong.com/Upload/editor/201708/20170811171936228_w.png'],
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
    logger.info(f'爬取方案{len(final_dic["pro"])}/2条数据')
    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'大研工控解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')