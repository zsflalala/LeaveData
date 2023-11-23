import json
import requests
from loguru import logger


def ControlTechniques(headers):
    final_dic = {'pro':[]}
    for i in range(1,9):
        if i == 1:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=69848'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生驱动与电机 MEV3000 交流驱动器'
            pro_dic['ProductImage'] = 'https://c.gongkong.com/UploadPic/Product/2014-5/2014052021415100003.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'多种通讯，方便交互','产品介绍':'多种通讯，方便交互MEV3000是最灵活多变、功能最丰富的MEV系列产品。可通过可选通信接口和定制化机器解决方案极大程度提升生产率。'}
            pro_dic['ProductDetail']['Feature'] = {'产品优势':{
                '保护人员和机器安全，最大程度保障正常运行时间':'• 两个安全扭矩关断端子，可实现安全系统集成，符合现代功能性安全标准• 无需外部组件，可节约空间和系统成本，提升机器可靠性• 安全跳闸时可快速重启',
                '机器集成灵活，提高生产率':'• 多种可选现场总线通信模块，可通过多种不同网络进行远程控制和诊断',
                '可选用直观的LCD键盘，简化使用过程':'• 中文显示，简化设置和监控过程• 诊断功能出众，可排查故障，最大程度保障运行时间',
                '增强的机器控制，极大程度提升生产量':'• 可借助增强的转子磁通控制功能提升电机性能',
                '定制化解决方案，可解决多种应用难题':'• 针对特殊应用，可借助定制化机器逻辑进行编程• 可预先编程，作为出厂设置• 可使用定制化功能，灵活地根据应用更新升级',
                '典型应用':'• 输送机、正排量泵、物料输送设备、切割设备、木材加工设备的速度控制，可实现必需的快速诊断',
                }}
            pro_dic['ProductDetail']['Parameter'] = {
                '主要参数':{
                    '重载额定值':'0.37 - 110 kW',
                    '电源相数':'400 V - 3 相',
                    '机器安全性':'2个安全扭矩关断端子',
                    '键盘':'无标配键盘',
                    '选项插槽':'1',
                    '远程键盘':'MEV-CI-LCD，可拆卸式中文LCD键盘;MEV-Remote Keypad，远程键盘支持IP66，需同时配置MEVAI-;485 Adaptor或MEV-CI-485 Adaptor',
                    'SI模块':'多种现场总线模块，包括Ethernet，Profibus DP, Devicenet,Canopen。MEV-SI-IO，额外的输入/输出',
                    '适配器':'MEV-AI-Backup Adaptor，支持SD卡；MEV-AI-485 Adaptor，提供RS485通讯接口；MEV-CI-485 Adaptor，提供RS485通讯接口',
                    '额定电压':'400 V (380 V - 480 V ± 10%) ✓',
                    '控制模式':'开环矢量控制或V/Hz感应电机控制✓；感应电机(RFC-A) 的开环转子磁通控制✓',
                }
            }
            final_dic['pro'].append(pro_dic)
        elif i ==2:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=69847'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生驱动与电机 MEV2000 交流驱动器'
            pro_dic['ProductImage'] = 'https://c.gongkong.com/UploadPic/Product/2014-5/2014052021363900001.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'方便选配，灵活集成','产品介绍':'方便选配，灵活集成MEV2000可通过附加的输入/输出和RS485接口增强连接的灵活性，增强的感应电机开环转子磁通控制(RFC-A)模式提高电机性能，实现快速设置，并可实现定制化。'}
            pro_dic['ProductDetail']['Feature'] = {'产品优势':{
                '定制化解决方案，可解决多种应用难题':'• 针对特殊应用，可借助定制化机器逻辑进行编程• 可预先编程，作为出厂设置• 可使用定制化功能，灵活地根据应用更新升级',
                '快速、简便的安装和配置':'• 标配高亮LED键盘• 键盘配备调速旋钮，方便控制运行速度• 参数设置方式符合中国工厂习惯• 可选配MEV-AI-Backup Adaptor，支持SD卡快速传输和备份参数• 可配置输入/输出，可接受脉冲信号• 可选用中文远程键盘，IP66，实现远程设置和诊断',
                '适用于恶劣的中国制造工厂环境的耐用型设计':'• 采用先进的冷却设计，配备获得专利的通风系统，能够更加高效地冷却驱动器，保护内部组件• 涂覆保护涂层• 已通过大量环境测试和认证• 过载率可达180 %，允许过载时间长达3秒• 电源电压的容差值大',
                '典型应用':'• 输送机、风扇、正排量泵和混料器的速度控制，可通过选配的ModBus RTU通信接口进行控制',
                }}
            pro_dic['ProductDetail']['Parameter'] = {
                '主要参数':{
                    '重载额定值':'0.37 - 45 kW',
                    '电源相数':'400 V - 3 相',
                    '机器安全性':'2个安全扭矩关断端子',
                    '键盘':'标配LED键盘，配备调速旋钮',
                    '选项插槽':'1',
                    '远程键盘':'MEV-Remote Keypad，需同时配置MEV-AI-Backup Adaptor',
                    'SI模块':'MEV-SI-IO，附加的输入/输出',
                    '适配器':'MEV-AI-Backup Adaptor，支持SD卡;MEV-AI-485 Adaptor，提供RS485通讯接口',
                    '额定电压':'400 V (380 V - 480 V ± 10%) ✓',
                    '控制模式':'开环矢量控制或V/Hz感应电机控制✓感应电机(RFC-A) 的开环转子磁通控制✓',
                }
            }
            final_dic['pro'].append(pro_dic)
        elif i == 3:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=69846'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生驱动与电机 MEV1000 交流驱动器'
            pro_dic['ProductImage'] = 'https://c.gongkong.com/UploadPic/Product/2014-5/2014052021302500001.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'易于使用，高性价比','产品介绍':'易于使用，高性价比;MEV1000是一款专为中国制造自动化应用而设计的易于使用的经济型开环驱动器。'}
            pro_dic['ProductDetail']['Feature'] = {'产品优势':{
                '快速、简便的安装和配置':'• 标配高亮LED键盘• 键盘配备调速旋钮，可方便控制运行速度• 参数设置方式符合中国工厂习惯• 可选配MEV-AI-Backup Adaptor，支持SD卡快速传输和备份参数• 可配置输入/输出，可接收脉冲信号',
                '适用于恶劣的中国制造工厂环境的耐用型设计':'• 采用先进的冷却设计，配备获得专利的通风系统，能够更加高效地冷却驱动器，保护内部组件• 涂覆保护涂层• 已通过大量环境测试和认证• 过载率可达180 %，允许过载时间长达3秒• 电源电压的容差值大',
                '缩小机器尺寸，节约成本':'• 紧凑设计，尺寸小巧',
                '定制化':'• 驱动器可通过定制化实现自定义参数默认值，便于机器快速出厂',
                '节约能耗':'• 能源损耗低，能效可高达98 %• 具有低功率待机模式',
                '典型应用':'• 输送机、风扇、泵和混料器的频率控制',
                }}
            pro_dic['ProductDetail']['Parameter'] = {
                '主要参数':{
                    '重载额定值':'230V: 0.37 - 2.2kW; 400V: 0.37 - 15kW',
                    '电源相数':'230 V - 1 相; 400 V - 3 相',
                    '键盘':'固定式LED键盘，配备速度调节旋钮',
                    '适配器':'MEV-AI-Backup Adaptor，支持SD卡',
                    '额定电压':'230 V (200 V - 240 V ± 10%) ✓; 400 V (380 V - 480 V ± 10%) ✓',
                    '控制模式':'开环矢量控制或V/Hz感应电机控制✓; 感应电机的转子磁通控制(RFC-A)',
                }
            }
            final_dic['pro'].append(pro_dic)
        elif i == 4:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=41149'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生 Unidrive M 变频器'
            pro_dic['ProductImage'] = 'http://fs.gongkong.com/files/product/201303/2013030616575500006.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'Unidrive M专为制造自动化而设计，1个产品系列，7种功能型号，能广泛应用于印刷、汽车、包装、激光切割、电缆制造等行业，帮助客户发挥最佳电机性能。','产品介绍':' Unidrive M专为制造自动化而设计，1个产品系列，7种功能型号，能广泛应用于印刷、汽车、包装、激光切割、电缆制造等行业，帮助客户发挥最佳电机性能。它使用开放式技术（以太网、CODESYS等）使客户能够创建更灵活的系统，它的智能机器结构包含以太网接口以及CoDeSys编程，与此同时，Unidrive M还充分满足了客户的五大需求：1、减少停机时间，增加机器产能；2、减小机器尺寸，最佳利用厂房面积；3、快速构建，降低复杂程度和成本；4、针对性的驱动具有更高的性能价格比；    5、快捷方便的改造升级。'}
            pro_dic['ProductDetail']['Feature'] = {}
            pro_dic['ProductDetail']['Parameter'] = {}
            final_dic['pro'].append(pro_dic)
        elif i == 5:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=21278'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生 Unidrive M600 交流驱动器'
            pro_dic['ProductImage'] = 'http://fs.gongkong.com/files/product/201104/2011040709201300005.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'用于感应电机和无传感器永磁电机的高性能驱动器：M600 可为无传感器感应电机和无传感器永磁电机控制提供更强的机器性能，从而实现动态、高效的机器操作。一个可选编码器端口可用于精确的速度闭环、数字锁/频率跟随应用。扩展 I/O、全球化的现场总线通讯以及编码器反馈选件使系统具有最大化的兼容性和灵活性。','产品介绍':''}
            pro_dic['ProductDetail']['Feature'] = {'产品优势':{
                '通过对所有交流电机的高性能控制使生产率最大化':'Unidrive M600 先进的 RFC 控制算法可实现最佳稳定性和控制，尤其是对大功率电机的控制。它可提供高带宽电机控制算法，具有62.5μs的电流环更新率，电机过载能力达 200%，适合重载型工业机械应用。',
                '与自动化系统灵活集成':'Unidrive M600 允许在驱动器内安装多达 3 个可选系统集成模块。这种增加的速度反馈、I/O 扩展和现场总线通信可在将机柜空间最小化的同时实现最大灵活性。SI-Encoder 选件可使 M600 为感应电机(RFC-A) 提供闭环转子磁通控制。',
                '增强型开放式板载 PLC':'Unidrive M600 具备一个带有实时任务功能的板载 PLC,可用于进行基本的逻辑控制、速度跟随以及数字锁，从而提高驱动器应用能力。通过将开放式 CODESYS 领先技术应用于机器控制编程，Unidrive M600 可供全世界的机器制造商简便地使用 。',
                '机器尺寸更小，成本更少':'Unidrive M600 具有紧凑的驱动器外形，就同功率而言是同类产品中尺寸最小的。Unidrive M600具备全部板载功能，诸如简单应用的可编程自动化、RS485通讯端口和1个遵从SIL3的安全转矩关闭端子，可提供一种强大的经济的解决方案，无需众多外部组件。',
                '可轻松访问机器控制功能':'软件工具、键盘和存储设备可轻松快捷地访问 Unidrive M 的机器控制功能以便配置、监控和诊断。',
                '典型应用':'通过高启动转矩的速度控制使其适用于挤出机、分切机、物料传输机、压缩机、制造业起重机、液压更换装置、比例控制、传动装置、卷绕（绕线机）、织物处理以及金属切割装置应用。',
                }}
            pro_dic['ProductDetail']['Parameter'] = {}
            final_dic['pro'].append(pro_dic)
        elif i == 6:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=19827'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生 Mentor MP直流驱动器'
            pro_dic['ProductImage'] = 'http://fs.gongkong.com/files/product/201101/2011011110402500002.png'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'艾默生新推出的Mentor MP直流驱动器集成了智能交流驱动器 Unidrive SP 的控制平台，最高支持20A的电机磁场，可选FXMP25扩展至25A。对于磁场电压极低、磁场电流大于25A的旧式电机，Mentor MP自身带有磁场模式，可用作磁场控制器。完全符合RoHS并通过全球认证，如CE和cULus。','产品介绍':'25A 至 7400A;　　400V / 575V / 690V　;　单象限或四象限操作'}
            pro_dic['ProductDetail']['Feature'] = {'产品优势':{
                '优点':'•   优化直流电机性能，提高系统可靠性并使用以太网和现场总线网络数字连接现代控制设备。　　•   继承艾默生 CT 交流驱动器系列的世界一流控制平台和软件工具，从而可在应用需要发生新变化时确保灵活修改交流驱动系统。　　•   标配最高支持 20A 的电机磁场控制器，可选 FXMP25 扩展至 25A。对于磁场电压极低、磁场电流大于 25A 的旧式电机，Mentor MP 自身带有磁场模式，可用作磁场控制器，不需另配其他部件。　　•   完全符合 RoHS 并通过全球认证，如 CE 和 cULus。•   允许驱动系统设计人员在驱动器内嵌入自动与运动控制，在我们的高性能驱动网络 CTNet 链接系统不同部分时消除通信延迟以免降低性能。　　•   设置快捷。系统配置既可采用可拆卸式键盘、智能卡，也可采用附赠 PC 调试软件以指导用户完成整个配置过程。　　•   理想的改造方案，确保与现有直流电机、电源、应用设备和通信网络轻松集成，给您的应用带来新性能和新变化。　　•   设计保证现有 Mentor II 客户可轻松迁移至新平台。同时保留所有电源端子位置和安装点并开发新软件工具以辅助驱动器参数和程序传输。　　艾默生 CT 已经申请专利以保护 Mentor MP 的独特设计。　　电源和控制间的电隔离是交流驱动器的标准功能之一，可在发生故障时保护控制电路和所接设备免受电路高压损坏。　　Mentor MP 采用独创技术实现电隔离而不会影响性能或可靠性。',
                '合规性':'• 在 40˚C (104˚F) 下最大湿度为 95%（无冷凝）　　• 环境温度介于-15至 40˚C（5˚F 至 104˚F），降额使 用允许达到55˚C (131˚F)　　• 海拔高度：0 至 3000m，在 1000m 到 3000m 范围 内，每 100m 降额 1%　　• 振动：按照IEC 60068-2-64 进行测试　　• 机械冲击：按照 IEC 60068-2-29 进行测试　　• 存放温度-40 至 70˚C（-40˚F 至 158˚F）　　• 电磁抗干扰性符合 EN 61800-3 和 EN 61000-6-2　　• 槽口抗干扰性符合 IEC60146-1-1 A 类　　•  IEC 61800-5-1 电气安全　　•  IEC 61131-2  I/O　　•  EN 60529 进入防护　　•  UL508C　　•  EN 61000-6-4 EMC  　　- 选配 EMC 滤波器　　• 符合 RoHS 标准　　注意：选配 EMC 滤波器的规格可向艾默生 CT 供应商索取。',
                '应用场合':'我们在各行各业的丰富经验证明我们是直流解决方案的理想合作伙伴。　　典型应用场合包括：　　•   金属　　•   印刷　　•   物料搬运　　•   橡胶和塑料　　• 造纸　　• 起重机和吊车　　•   采矿　　•   电梯　　•   用于交流驱动系统整流回馈直流母线',
                }}
            pro_dic['ProductDetail']['Parameter'] = {}
            final_dic['pro'].append(pro_dic)
        elif i == 7:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=18157'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生 Digitax ST系列伺服驱动器'
            pro_dic['ProductImage'] = 'http://fs.gongkong.com/files/product/201009/2010090911312700004.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'艾默生全新的Digitax ST系列伺服驱动器具有智能、小巧、灵活、功能强大和高动态响应等特点。额定电流从1.1A到8A，额定电压为单相或三相230V、三相400V。满足了现代精益制造的要求，实现规模小、智能化、快速响应、高度灵活的控制系统。','产品介绍':'为满足现代精益制造的要求，实现规模小、智能化、快速响应、高度灵活的控制系统，艾默生推出了全新的Digitax ST系列伺服驱动器。该系列伺服驱动器具有智能、小巧、灵活、功能强大和高动态响应等特点。额定电流从1.1A到8A，额定电压为单相或三相230V、三相400V。'}
            pro_dic['ProductDetail']['Feature'] = {'产品优势':{
                '功能强大':'除通用伺服驱动器的功能外，具有内置编程功能，可轻松实现逻辑控制、点位控制、电子齿轮、电子凸轮、高速位置捕捉等运动控制功能。有众多的功能模块可选。',
                '全内置编码器接口':'支持增量型、SinCos、Hiperface、EnDat、SSI等各种编码器。',
                '现场总线':'支持EtherCAT、SERCOS、CANopen、PROFIBUS DP、DeviceNet、Interbus、CTNet以及标准Ethernet等。',
                '轻松上手':'可使用CTSoft Index motion，IEC61131-3(类PLC编程)，PowerTools Pro（类BASIC编程）编程，任何应用工程师都可轻松入门。',
                '自动调谐':'通过测量机器的动态特性来自动优化控制环增益，使设备达到最佳性能。',
                '安装简单':'驱动器支持DIN导轨安装，控制端子易于插拔，卡口式模块安装无需专用工具。',
                '易于设置':'使用可插拔面板、智能卡或调试软件均可设置驱动器参数，并可在驱动器之间复制参数。',
                'Digitax ST的四种类型':'使用可插拔面板、智能卡或调试软件均可设置驱动器参数，并可在驱动器之间复制参数。',
                '典型应用':'● 印刷机● 包装机● 横切机● 纺织、线缆的卷绕装置● 数控机床● 飞剪● 物料搬运● 点胶● XY工作台● 快速精确的流体配料● 同步输送机● 冲孔● 高速贴标机● 其他应用',
                }}
            pro_dic['ProductDetail']['Parameter'] = {}
            final_dic['pro'].append(pro_dic)
        elif i == 8:
            url = 'https://c.gongkong.com/PhoneVersion/ProductDetail?pId=13044'
            resp = requests.get(url=url,headers=headers)
            pro_dic = {}
            pro_dic['ProductName'] = '艾默生 智能精巧型Unidrive SP 0型驱动器'
            pro_dic['ProductImage'] = 'http://fs.gongkong.com/files/product/200912/2009121110053500015.jpg'
            pro_dic['ProductUrl'] = url
            pro_dic['ProductHTML'] = resp.text
            pro_dic['ProductJSON'] = ''
            pro_dic['FirstType'] = ''
            pro_dic['SecondType'] = ''
            pro_dic['ProductDetail'] = {}
            pro_dic['ProductDetail']['Description'] = {'产品简介':'近日，艾默生驱动与电机推出了市场上最小巧、最智能化的交流驱动器Unidrive SP0。',                                                    '产品介绍':' 近日，艾默生驱动与电机推出了市场上最小巧、最智能化的交流驱动器Unidrive SP0。新的Unidrive SP0型驱动器的功率范围为0.37KW-1.5KW，具有200V单相/3相和400V3相，其创新的设计和优化的性能使这款驱动器非常适合高端的机械控制，并可极大地改善机械性能。其小巧的机身可以减少控制柜的尺寸，而且驱动器上的两个插槽具有极大的灵活性，可最大化的满足客户的应用需求。新的Unidrive SP 0型驱动器的主要特点：● 内置EMC滤波器● 2个选件插槽● 安全Torque off输入● 24V备用电源● 智能卡● 可插拔键盘● 通用编码器输入● 编码器输出● 高精度的模拟和数字I/O● 用于编程的PC端口● 48V低压直流供电● 易于安装● 可选内部制动电阻另外，Unidrive SP0型驱动器还具有与SP系列其他驱动器一样的高级功能、通用的电机控制模式以及友好的用户界面。Unidrive SP系列驱动器能为0.37KW至1.9MW所有交流感应电机、伺服电机和同步电机的控制提供完整的解决方案。能广泛应用在纺织、起重、造纸、印刷包装、金属加工、塑胶、冶金、线缆、供水、暖通、制造、卷扬等对机械控制要求较高的环境中。关于艾默生工业自动化艾默生工业自动化是Emerson公司所属业务品牌，提供技术领先的生产解决方案，包括机械、电力及超声波等，为全球多种多样的行业提供最先进的工业自动化。该业务品牌广泛的产品和系统应用 于生产过程和设备，包括运动控制系统、物料连接、精密清洗、物料测试、液压控制阀、交流发电机、马达、机械动力传输驱动器和轴承等。了解详细信息，请浏览www. emerson.com 或 www.emerson-ap.com  关于Control TechniquesControl Techniques 是艾默生工业自动化的下属公司。我们的专项是驱动器的设计,生产和工程应用,并提供技术支持和售后服务.我们的目标是确保客户在使用了CT优良可靠的产品后, 能降低生产成本,提高生产效率.CT业务遍及全球，其生产与研发机构集中于欧洲与亚洲，另有驱动与应用中心分布在35个国家的50个地区。驱动与应用中心主要为客户提供本地销售，服务与设计技术.在中国, 艾默生驱动与电机（属于CT）拥有30个办事处和代表处分布于中国各省城区域,如深圳，上海，北京等。凭借在工业自动化行业领先的驱动技术以及丰富的经验，艾默生CT提供完整的全方位的配套驱动解决方案，从通用到高性能的直交流驱动器、伺服、伺服电机、PLC及触摸屏产品。了解详细信息，请浏览www. controltechniques.com 或 www.emerson-ct.cn'}
            pro_dic['ProductDetail']['Feature'] = {}
            pro_dic['ProductDetail']['Parameter'] = {}
            final_dic['pro'].append(pro_dic)
    return final_dic

if __name__ == '__main__':
    logger.add('runtime.log')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 
    }
    final_dic = ControlTechniques(headers=headers)
    filename=f'艾默生驱动与电机产品{len(final_dic["pro"])}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f'共爬取{len(final_dic["pro"])}条数据，存储在{filename}中.')
    