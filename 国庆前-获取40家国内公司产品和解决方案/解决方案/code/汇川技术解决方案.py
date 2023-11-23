import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


def parse_solution(headers,id,firstTypeName,secondTypeName): 
    solu_list = []
    url = f'https://www.inovance.com/portal-front/api/solution/info/{id}?showChannel=2'
    resp = requests.Session().get(url,headers=headers)
    result = resp.json()['result']
    for case in result:
        solu_dic = {}
        info = case['info']
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = f'https://www.inovance.com/portal/solution/info/{id}'
        solu_dic['SolutionHTML'] = ''
        solu_dic['SolutionJSON'] = info
        solu_dic['SolutionName'] = info['titleSlogan']
        solu_dic['方案概述'] = info['solutionDetail']
        solu_dic['方案优势'] = {}
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solutionAdvantage = info['solutionAdvantage']
        if solutionAdvantage:
            tree = etree.HTML(solutionAdvantage)
            h3_list,content_list = [],[]
            for item in tree.xpath('.//h3/text()'):
                h3_list.append(item.strip())
            for item in tree.xpath('.//p/text()'):
                content_list.append(item.strip())
            assert len(h3_list) >= len(content_list)
            for i in range(len(h3_list)):
                if i >= len(content_list):
                    solu_dic['方案优势'][h3_list[i]] = ''
                else:
                    solu_dic['方案优势'][h3_list[i]] = content_list[i]
        solutionStructureNoneTag = info['solutionStructureNoneTag']
        solutionStructureNoneTag = json.loads(solutionStructureNoneTag)
        structImg = solutionStructureNoneTag['structImg']
        if structImg != []:
            construct_img = urljoin(url,structImg[0]['url'])
            solu_dic['方案组成'].append(construct_img)
        solu_list.append(solu_dic)
    return solu_list

def parse_special(headers,firstTypeName,secondTypeName,id):
    solu_list = []
    if firstTypeName == '汽车零部件':
        url = 'https://www.inovance-automotive.com/solve/index8.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        tree = etree.HTML(resp.text)
        solu_dic = {}
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '新能源乘用车解决方案'
        solu_dic['方案概述'] = '汇川联合动力新能源乘用车解决方案可根据不同车型提供电机、电控、电源及动力总成多种产品组合的搭配方案，在确保驾驶的安全性、高效性及经济性的同时兼顾整车匹配的灵活性，方案适用于A00级、A0级、A级、B级等不同级别的纯电、混动、增程式车型。'
        solu_dic['方案优势'] = {
            '高功率密度':'结构紧凑，轻量化设计，高功率密度提升整车续航里程',
            '高灵活性':'采用模块化、平台化设计，可根据整车需求灵活选配',
            '高安全性':'采用成熟技术及一系列安全功能，保证车辆驾驶的安全可靠'
        }
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        swiper_slide_list = tree.xpath('.//div[@class="swiper-slide"]')
        for swiper_slide in swiper_slide_list:
            img = urljoin(url,swiper_slide.xpath('./div[1]/img/@src')[0])
            title = swiper_slide.xpath('./div[2]/h1/text()')[0]
            content = swiper_slide.xpath('./div[2]/ul//text()')
            content = ';'.join([item.strip().replace(' ','') for item in content])
            temp_dic = {title:content,'img':img}
            solu_dic['方案组成'].append(temp_dic)
        solu_list.append(solu_dic)
    elif secondTypeName == '硅晶':
        solu_dic = {}
        url = 'https://www.inovance-iv.cn/taoci/13532272.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '汇流焊焊点检测系统'
        solu_dic['方案简介'] = '应对产品流出后检测导致大量报废问题，以及终端人员检测遗漏问题，针对汇流焊设备不同工艺，开发了汇流焊焊点在线检测系统，通过深度学习分割焊点，再通过传统算法对焊接饱满度进行量化分析，同时能够支持不同组件的快速换型（20min），简单的参数调节，简洁的Job界面，应用于TOP光伏组件终端。'
        solu_dic['优势&特点'] = {
            '误检率≤0.5%，较高的检测效率不影响汇流焊设备节拍':'',
            '快速的换型切换：已建型号≤1min，未建型号≤20min':'',
            '简易的调节方式，快速的功能实现':''
        }
        solu_dic['应用领域'] = [{
                'content':'光伏组件终端企业。',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818170330-8.png',
                'type':'image'
            }
        ]
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/taoci/13532301.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '汇流焊焊疤检测系统'
        solu_dic['方案简介'] = '应对产品流出后检测导致大量报废问题，以及终端人员检测遗漏问题，开发了汇流焊焊疤在线检测系统，识别到焊接问题时NG报警，同时能够支持不同组件的快速换型（20min），简单的参数调节，简洁的Job界面，应用于TOP光伏组件终端。'
        solu_dic['优势&特点'] = {
            '误检率≤0.5%，较高的检测效率不影响汇流焊设备节拍':'',
            '快速的换型切换：已建型号≤1min，未建型号≤20min':'',
            '简易的调节方式，快速的功能实现':''
        }
        solu_dic['应用领域'] = [{
                'content':'光伏组件终端企业。',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818165951-6.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/taoci/17124251.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '点胶后胶路检测'
        solu_dic['方案简介'] = '涂胶后的检测有助于实时反馈涂胶质量。当发生长度不足、平均宽度不足、胶路断开等情况，会影响粘合效果；当发生胶路过宽或过长会导致溢胶，形成干扰，影响美观。基于汇川视觉自主研发的Kinovision控制平台，实现了胶路的长度、宽度、平均宽度、轨迹相似度等检测。胶路模板绘制简单，学习快速，设备工程师也能够迅速完成方案的调试。'
        solu_dic['优势&特点'] = {
            '胶路绘制简单，简单培训即可上手':'',
            '胶路检测项完备，长宽、断开、轨迹均可检测':'',
            '检测结果清晰，分类方法完善':'',
            '学习后自动填写参数，根据要求简单修改即可':''
        }
        solu_dic['应用领域'] = [{
                'content':'保护盖涂胶检测等。',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818154353-3.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/taoci/17121087.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '硅片破损检测系统'
        solu_dic['方案简介'] = '应对劳动力成本攀升和自动化升级的需要，针对硅晶行业光伏清洗插片机，工艺可能导致电池片破损，开发了电池片破损检测系统。该系统兼容最大210mm电池片尺寸，同时检测3通道，在硅片运行中进行飞拍检测，不影响设备节拍，参数调节方便，应用于光伏清洗设备TOP客户'
        solu_dic['优势&特点'] = {
            '误检率≤0.5%，飞拍检测，单道产能4000 PCS/h':'',
            '快速的换型切换：≤20min':'',
            '最小可检测缺陷≥0.5mm':''
        }
        solu_dic['应用领域'] = [{
                'content':'单片电池片生产企业。',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818170540-10.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)
    elif secondTypeName == '锂电':
        solu_dic = {}
        url = 'https://www.inovance-iv.cn/li/13532169.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '动力电池卷绕机项目方案'
        solu_dic['方案简介'] = '卷绕机是锂电池成型的主要设备，通过驱动卷针将正负极片和隔膜按照特定的次序卷绕从而形成电芯，在此过程中，需使用视觉进行对齐度纠偏，同时识别相机视野范围内的涂布、隔膜缺陷，以保证产品质量。我司采用KINOVISION视觉检测平台对卷绕过程中的阴阳极距离和整体电芯的尺寸进行检测，同时创新采用深度学习相关算法，实时检测涂布和隔膜的各类缺陷，提升产品质量，该方案已批量应用于锂电客户。'
        solu_dic['优势&特点'] = {
            '业内首创的AI算法，稳定检出各类隔膜、极片缺陷，误捡率≤0.1%，缺陷检出率>99.9%':'',
            '测量检测精度二次元对比<±0.12mm，GRR≤10%':'',
            '简易的调节方式，快速的功能实现':''
        }
        solu_dic['应用领域'] = [{
                'content':'新能源汽车、储能市场的电池生产',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/f35b2005-b57f-40e6-90af-b7e3d5cd2226.png',
                'type':'image'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818165154-5.png',
                'type':'image'
            }
        ]
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/li/13532216.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '极片AI缺陷检测方案介绍'
        solu_dic['方案简介'] = ''
        solu_dic['优势&特点'] = {}
        solu_dic['应用领域'] = [{
                'content':'检测性能：算法部分的设计基于深度学习最新理念和架构，可用于检测形态各异的缺陷，检出能力强，最小检测面积4*4像素大小的缺陷（0.1mm^2），8192*6000图像大小的检测耗时40-50ms。',
                'type':'text'
            },{
                'content':'多分类性能:（在单分类的基础上区分出检测缺陷的种类，可用于设备工艺的改进）',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818164617-1.png',
                'type':'image'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818164940-4.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/li/13532231.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '激光清洗机视觉检测方案'
        solu_dic['方案简介'] = '激光清洗机是消费类锂电池成型的主要设备，用于电池极片焊接前极耳焊接位置的涂层清洗，在清洗后需对清晰区域的尺寸和残留、针孔和氧化等缺陷进行检测，为此，我司采用KINOVISION视觉平台，实时在线检测清洗区域的不良，有效控制产品质量，大量的应用于数码类锂电池的生产中。'
        solu_dic['优势&特点'] = {
            '较高的检测效能和检测精度：效率20ppm，精度±0.04mm':'',
            '快速的换型切换≤1min':'',
            '简易的调节方式，快速的功能实现':''
        }
        solu_dic['应用领域'] = [{
                'content':'手机，电脑，智能穿戴设备的电池生产',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/090dc984-000d-4f89-a468-68fac72f7eb1.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)
    elif secondTypeName == '食品饮料':
        solu_dic = {}
        url = 'https://www.inovance-iv.cn/guan/13532082.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = 'PET灌装缺陷检测系统'
        solu_dic['方案简介'] = '在灌装行业生产效率不断提升、人力成本不断增加、产品质量要求不断提高的趋势下，汇川视觉创新性地使用视觉图像技术&深度学习技术，开发出一套基于行业整线工艺的视觉检测解决方案，从而有效提升了客户出厂产品品质，节省人工，提升产能效率，推动行业的自动化、智能化发展。该方案目前已在国内各大龙头企业批量使用，得到客户一致好评。'
        solu_dic['优势&特点'] = {
            '基于工艺的整线解决方案，关注生产的每一个细节':'',
            '各检测工位采用深度学习技术，使用方便、设置简单，调节参数<2个':'',
            '检测效果好，各工位检出率≥99.98%，误检率<0.3%':'',
            '自动调节+检测参数标准化，实现产品快速切换且快速稳定，换产单设备切换时间<2min':'',
            '详尽的报表输出功能，为生产设备工艺优化及效率提升提供有效数据支撑':''
        }
        solu_dic['应用领域'] = [{
                'content':'食用油灌装、调味品灌装、饮料灌装、纯净水灌装等',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818162404-5.png',
                'type':'image'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/7c72ebab-d9dd-422c-b38c-f5bf95fe2243.png',
                'type':'image'
            }
        ]
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/taoci/17122773.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '易拉罐检测方案'
        solu_dic['方案简介'] = '易拉罐的缺陷主要产生在运输过程中，运输易导致瓶口破损，罐内异物，挤压变形等多方面缺陷。基于客户工艺，可在罐装前设置空罐在线检测系统，针对罐口磕碰，罐壁凹陷变形，罐底异物破洞进行检测，确保生产出符合市场标准的产品，设备检测精度高、速度快，24小时不间断检测，可靠性高。'
        solu_dic['优势&特点'] = {'误检率≤0.1 %，检出率≥99.98%，检测效能最高达60000BPH。':''}
        solu_dic['应用领域'] = [{
                'content':'易拉罐罐口、罐身、罐底等多方面缺陷',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818162742-6.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/guan/13532092.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '行业应用视频'
        solu_dic['方案简介'] = ''
        solu_dic['优势&特点'] = {}
        solu_dic['行业应用视频'] = [{
                'content':'https://omo-oss-video.thefastvideo.com/portal-saas/new2021123120352318583/cms/vedio/b0dc797f-1b63-4d49-9bf1-d78490ef35cf.mp4',
                'type':'video'
            }
        ]
        solu_list.append(solu_dic)
    elif secondTypeName == '印刷&包装':
        solu_dic = {}
        url = 'https://www.inovance-iv.cn/tp/1.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '特殊薄形圆片外观边部检测组件'
        solu_dic['方案简介'] = '本产品专用于检测特殊薄形圆片工件的侧面的一次成像光路组件，譬如纪念币、纽扣电池及其它各种精密加工件。因具有双曲面特性设计，可将薄形侧面放大观测、相比普通侧视镜头可获取更多的侧面信息。'
        solu_dic['优势&特点'] = {
            '正面和侧面一次成像、标准对应1"CCD和1.1"CCD':'',
            '采用双曲面设计、扩大侧面的视野、提取更多地侧面信息':'',
            '光源光路一体设计，安装调试简便':'',
            '更换光源后也可对工件内壁实施放大观测(OPTIONAL)':''
        }
        solu_dic['应用领域'] = [{
                'content':'造币、精密薄形零件（电子/机械）',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/48aebf20-ce57-49a6-960e-1754cf32c4a7.png',
                'type':'image'
            }
        ]
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/taoci/17120841.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '轧盖质量检测'
        solu_dic['方案简介'] = '轧盖机为西林瓶联动线的核心设备，该设备广泛用于医药领域，但西林瓶在轧盖过程中易出现密封不良现象，我司针对此领域推出了基于KINOVISION视觉平台的在线高速轧盖检测方案，有效降低胶塞缺失、波纹、裂缝、未封口、无盖等不良产品外流现象。'
        solu_dic['优势&特点'] = {
            '完美兼容各类大小尺寸西林瓶，抽检变全检':'',
            '高速运行环境下，实现99.5%的检出率，检测最小缺陷达1mm²':'',
            '高速实时检测，检测效率≥500 pcs/min':'',
            '多相机组合方案有效解决客户产线空间问题':'',
        }
        solu_dic['应用领域'] = [{
                'content':'适用于西林瓶、口服液等铝盖轧盖；',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818160500-4.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/yin/13527331.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '激光清洗机视觉检测方案'
        solu_dic['方案简介'] = '多列机、装盒机为条袋包装的核心设备，该设备广泛用于医药、保健品领域，此领域对于三期码的完整性和正确性有极高要求，需要确保交付无喷码缺陷的产品，我司针对此领域推出了基于深度学习的OCR全识别方案，该方案方便作业，稳定性好，调试、换型参数少，有效包证三期码的完整性和正确性。'
        solu_dic['优势&特点'] = {
            '采用领先的深度学习技术，实现无参化':'',
            '喷码识别准确率99.98%':'',
            '兼容不同颜色的背景':'',
            '实时数据可视化，异常产品可追溯':''
        }
        solu_dic['应用领域'] = [{
                'content':'适用激光、油墨和钢印类喷码;适用任何铁质、PE/PET、纸质等材质的专业包装',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/e063ee6c-3276-4174-a055-d089bcdf3047.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/yin/13527994.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '玻璃瓶空瓶外观检测'
        solu_dic['方案简介'] = '制瓶机为玻璃瓶生产核心设备，该设备广泛用于医药、食品领域。玻璃烧制过程受温度、湿度、原料、设备异常的影响，成型后的玻璃瓶会出现气泡、结石、黑点、裂纹、气线、磕碰、脏污等缺陷，我司针对此领域推出了基于深度学习的空瓶缺陷检测方案，该方案作业便捷，调试、换型时间短，检测效率高，有效降低不良品外流。'
        solu_dic['优势&特点'] = {
            '采用业内深度学习技术，实现缺陷检测无参化，稳定性比传统视觉方式提升一倍':'',
            '行业高精度，检出率≥99.9%，检测最小缺陷可达0.02mm²':'',
            '高速实时检测，检测效率≥50 pcs/min':'',
            '完美兼容各类尺寸西林瓶；彻底改变客户现有工艺，抽检变全检':''
        }
        solu_dic['应用领域'] = [{
                'content':'管制瓶、玻璃成型类，检测制瓶后的成型缺陷',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/52cd741e-8706-47a8-8aca-8451dfc90b29.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/yin/13528025.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '盒&箱内点数'
        solu_dic['方案简介'] = '装盒机为条袋包装的核心设备，该设备广泛用于医药、保健品领域，对于单条克重较轻的条包电子称重器不能有效检测少装，往往引发客诉的情况，我司针对性的推出了基于深度学习的盒内点数方案，其作业/调试便捷、调试参数少，检测准确，可以有效防止缺数产品外流，解决盒内缺数问题。'
        solu_dic['优势&特点'] = {
            '独创深度学习工具，适应样品密集、分散等复杂的场景':'',
            '缺包检测精度高，指标可达99.98%':'',
            '检测效率高，单个检测耗时小于200ms':'',
            '兼容不同材质包装，不受环境光线影响':''
        }
        solu_dic['应用领域'] = [{
                'content':'可检测位于罐体内、箱体内、纸壳内产品数量',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/bac2c87e-138c-4594-b2a3-4aa41a26f406.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/yin/13531753.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '多列机&装盒机喷码识别方案'
        solu_dic['方案简介'] = '多列机、装盒机为条袋包装的核心设备，该设备广泛用于医药、保健品领域，此领域对于三期码的完整性和正确性有极高要求，需要确保交付无喷码缺陷的产品，我司针对此领域推出了基于深度学习的OCR全识别方案，该方案方便作业，稳定性好，调试、换型参数少，有效包证三期码的完整性和正确性。'
        solu_dic['优势&特点'] = {
            '采用领先的深度学习技术，实现无参化':'',
            '喷码识别准确率99.98%':'',
            '兼容不同颜色的背景':'',
            '实时数据可视化，异常产品可追溯':''
        }
        solu_dic['应用领域'] = [{
                'content':'适用激光、油墨和钢印类喷码;适用任何铁质、PE/PET、纸质等材质的专业包装',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/e063ee6c-3276-4174-a055-d089bcdf3047.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)
    elif secondTypeName == '手机':
        solu_dic = {}
        url = 'https://www.inovance-iv.cn/3c/13526699.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '对位贴合应用'
        solu_dic['方案简介'] = '3C生产中执行机构种类多，非标对位类型多，对位误差难以解耦。我司的Kinovision视觉应用平台支持多种通讯协议，支持标准或非标执行机构，包括机器人、UVW、XYθ模组等，具备脚本编程，具有极大的灵活性于高度的适应性。其特有的误差验证工具和误差排除标准流程，满足单平移对位、单相机双工位对位等非标对位需求，高精度地满足客户误差解耦的需求。'
        solu_dic['优势&特点'] = {
            '支持脚本编程，配置灵活，能配合多种执行机构，适应非标对位需求':'',
            '专业的误差验证工具，快速进行精度解耦':'',
            '有统计工具，可方便输出CPK、GRR、相关性等多种指标':'',
            '精度达±0.075~0.1mm，CPK>1.33 ':''
        }
        solu_dic['应用领域'] = [{
                'content':'手机、平板/笔电、车载、TV等对位应用',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/d6a78f90-cc80-40a3-a29f-dff20b2356d4.png',
                'type':'image'
            }
        ]
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/3c/13527292.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '焊接缺陷检测'
        solu_dic['方案简介'] = '电机转子的焊接，当发生虚焊、偏焊、漏焊等情况时，可能导致产品故障，例如汽车的大范围召回等。基于汇川视觉自主研发的KINOVISION控制平台，采用2000w分辨率相机+多色AOI光源+深度学习的方案，实现了从图像判断焊锡质量。该方案相比于3D成本大大降低，且调试简单，能够区分具有细微形态差别的焊点。'
        solu_dic['优势&特点'] = {
            '深度学习缺陷检测技术，可学习人工标准，兼容形态变化':'',
            '定制化光学方案，实现大视野下小焊点的检测':'',
            '漏检率<0.02% ，误检率<3%':'',
            '检测过程无参数化，极大降低应用难度':'',
        }
        solu_dic['应用领域'] = [{
                'content':'电机转子焊接检测等；',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/7271ef1e-37b7-4dab-9370-4ecd04260f02.png',
                'type':'image'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/image-20220818151403-2.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/3c/13527306.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '五轴控制类应用'
        solu_dic['方案简介'] = '科技产品精致外型是产品重要的买点。而产品生产过程中，异形产品的检测精度、检测难度更高，使得传统的非异形的三轴、四轴解决方案难以满足客户需求，汇川凭借在工控行业的多年积累，推出了五轴平台下控制&视觉一体化解决方案，替代平面轨迹，实现空间轨迹的点胶、切割、检测，匀线速度的高精度五轴同步运动。同时该检测方案入门简单，通过简单示范教学即可培训上岗。'
        solu_dic['优势&特点'] = {
            '控制/视觉一体化解决方案，调试简便':'',
            '五轴联动+视觉引导，满足3D轨迹需求':'',
            '五轴示教变为平面示教，只需要30分钟即可完成':'',
            '运动控制+视觉取点，实现五轴匀速同步运动':''
        }
        solu_dic['应用领域'] = [{
                'content':'五轴点胶机、五轴切割机、异形件多曲面缺陷检测机等',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/24629794-0b3b-4a4e-a207-f77db2db0871.png',
                'type':'image'
            }
        ]
        solu_list.append(solu_dic)
    elif secondTypeName == 'TP':
        solu_dic = {}
        url = 'https://www.inovance-iv.cn/tp/13526350.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['FirstType'] = firstTypeName
        solu_dic['SecondType'] = secondTypeName
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '整线API检测方案'
        solu_dic['方案简介'] = '应对劳动力成本攀升，质量要求的逐步提高，创新性运用深度学习技术，针对显示行业工艺过程中的各类缺陷，开发了全工艺段API视觉检测系统，漏检率稳定控制在0.3%以内，大批量应用于各个TOP级面板、模组、整机客户。'
        solu_dic['优势&特点'] = {
            '漏检率<0.3% ；过筛率<10% ':'',
            '兼容0.9-75寸，支持OLED屏检测':'',
            '换型时间：新型号产品<1h  /  旧产品型号<0.5h':''
        }
        solu_dic['应用领域'] = [{
                'content':'智能穿戴、手机、平板/笔电、车载、TV;创新性采用良品深度学习算法模式，新型号换型时只需按正常检测操作放置50片产品，即可完成产品参数自学习过程， 实现新型号换型耗时<1h，让生产厂商真正自主能用、会用、用好API设备。',
                'type':'text'
            },{
                'content':'https://omo-oss-image.thefastimg.com/portal-saas/new2021123120352318583/cms/image/69bcaee3-6bbb-4ee7-95de-941e56a7bdae.png',
                'type':'image'
            }
        ]
        solu_dic['方案组成'] = []
        solu_dic['ProductUrl'] = []
        solu_list.append(solu_dic)

        url = 'https://www.inovance-iv.cn/3c/13527292.html'
        resp = requests.get(url=url,headers=headers)
        resp.encoding = 'utf-8'
        solu_dic['SolutionUrl'] = url
        solu_dic['SolutionHTML'] = resp.text
        solu_dic['SolutionJSON'] = ''
        solu_dic['SolutionName'] = '行业应用视频'
        solu_dic['方案简介'] = ''
        solu_dic['优势&特点'] = {}
        solu_dic['应用领域'] = [{
                'content':'https://omo-oss-video.thefastvideo.com/portal-saas/new2021123120352318583/cms/vedio/47f8153e-3e30-4c29-96ac-f5c9395622ee.mp4',
                'type':'video'
            }
        ]
        solu_list.append(solu_dic)
    return solu_list

def get_solution(url,headers):
    final_dic = {'pro':[]}
    resp = requests.Session().get(url=url,headers=headers)
    result = resp.json().get('result')
    for firstType in result:
        firstTypeName = firstType['typeName']
        children = firstType['children']
        for child in children:
            remark = child['remark']
            id = child['id']
            secondTypeName = child['typeName']
            if not remark:
                solu_list = parse_solution(headers,id,firstTypeName,secondTypeName) 
                final_dic['pro'] += solu_list
            else:
                solu_list = parse_special(headers,firstTypeName,secondTypeName,id)
                final_dic['pro'] += solu_list
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log',retention='1 day')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Cookie':'Hm_lvt_df77af9ca30581ae15b09368240f63fc=1693819809,1693971458,1695628145; once=2023-9-26; Hm_lpvt_df77af9ca30581ae15b09368240f63fc=1695691876',
        'Referer':'https://www.inovance.com/portal/solution?active=0',
    }
    url = 'https://www.inovance.com/portal-front/api/solution/index'
    final_dic = get_solution(url,headers)
    
    filename,dic = 'temp.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')
