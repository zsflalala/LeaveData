import json
import requests
from lxml import etree
from loguru import logger
from urllib.parse import urljoin


@logger.catch
def get_solution(headers):
    final_dic = {'pro':[]}

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e6%a0%b7%e5%93%81%e5%88%87%e5%89%b2%e5%99%a8/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    firstTypeName = '样品切割器'
    Description = [
        {
            'content':'Alpha 的样品切割器可在几秒钟内生产出恒定体积的橡胶样品。 对于流变仪和粘度计测试的可重复性至关重要的 MDR、RPA 和 MV 仪器，定容样品是理想的选择。 有两种样品切割器可供选择，样品可以完美地放入相应的样品托盘中。双作用气动样品压机——在几秒钟内获得橡胶样品。紧凑的尺寸– 非常适合有效利用工作台空间和仪器放置。双手安全触摸开关——利用光学传感器，需要两只手来激活机器。 这提高了操作员的安全性，并且不需要防护罩。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3106_900-811x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3090_900-811x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3101_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3091_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Alpha-Sample-Cutter-Brochure.pdf',
            ],
            'type':'img'
        },{
            'content':'<table><tbody><tr><td>电气：</td><td>100/240 VAC，50/60 Hz，最大 10 瓦</td></tr><tr>			<td>空气压力：</td>			<td>83 至 115 psi（5.6 至 8.0 kg/cm2）</td>		</tr>		<tr>			<td>方面：</td>			<td>宽 28 厘米（11 英寸），高 55 厘米（21.8 英寸），深 34 厘米（13.4 英寸）</td>		</tr>		<tr>			<td>外壳尺寸：</td>			<td>70 x 48 x 70 厘米</td></tr><tr><td>重量：</td><td>净重 35 公斤（77 磅），毛重 53 公斤（117 磅）</td>		</tr></tbody></table>',
            'type':'table'
        },
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e6%80%bb%e7%90%86-mdr/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    firstTypeName = 'Premier MDR'
    Description = [
        {
            'content':'如何将 Premier MDR 与所有其他人进行比较。更硬的密封件具有低摩擦，可防止滑动和泄漏，并确保不会丢失信号。 另外，它们的使用寿命更长。油饱和推力轴承使用寿命更长，无需润滑，整体维护成本更低。标准压力传感器允许测量泡沫性能以确定压力是否通过测量发生变化。 这使您能够优化配方并减少错误。独立的触摸屏用户界面——用于仪器管理的工作台和用于数据分析的在线管理器。 我们的定制电子设备为您提供真正的多任务处理。 与其他人使用的缓慢 PLC 不同，无需等待测试完成即可查看数据。您可以信赖的扭矩标准。 Alpha 致力于可追溯的扭矩标准，以确保您的仪器得到准确校准。 其他人使用更便宜的扭矩标准（他们不喜欢分发），这些标准具有不可接受的误差范围，并且需要捏造因素才能使它们“正确”出来。从您的 Premier MDR 中获得更多价值扩展 Premier MDR 功能的选项。Rapid Change™偏心轮无需校准即可简单快速地改变摆动角度（0.2、0.5、1、3 和 7.17 度）。 我们以一个多小时的优势击败了比赛！智能密封™。 可选的上模组件可消除传统的弹性密封件，同时保持封闭的加压腔，以提高长期数据稳定性并减少对扭矩校准的需求。轻松自动化。 我们的 3 侧开放式外壳可以轻松添加多种自动化选项，以支持小批量到大批量生产需求。 我们紧凑、轻便的样品输送系统提供业内最可靠的样品传输系统。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Premier-MDR-2_900-852x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Premier-MDR-1_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Custom-electronics_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Advance-die-cooling_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Better-heating-control_Alpha-Tech_211130_0128_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Dynamic-Symmetry-alignment_900-200x300.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Cast-aluminum-frame_900-224x300.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Drawer_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha_MDR_Flyer_FA.pdf',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-Premier-MDR_Declaration-of-Conformity-CE-Certification.pdf',
            ],
            'type':'img'
        },{
            'content':'<table><tbody><tr><td>频率：</td><td>100 cpm (1.67 赫兹)</td></tr><tr><td>温度范围：</td><td>环境温度为 446°F (230°C)</td></tr><tr><td>拉紧：</td><td>0.5 标准（7%）； 0.2、1.0、3.0 和 7.17 度</td></tr><tr><td></td><td>(2.8%、14%、42% 或 100%) 可用 ML、MH、MH-ML、Ts1、Ts2、</td></tr><tr><td>在船上：</td><td>T10、T50、T90、S？ 在 ML，S? 在 MH、TD 在 ML、TD 在 MH、最大固化速率、最大固化速率时间、压力点 PH-PL 和压力时间点</td></tr><tr><td>测试标准：</td><td>符合 ASTM D5289、ISO6502 和 DIN 53529</td></tr><tr><td>电气：</td><td>100/110/120/130 VAC+/- 10%, 60 +/- 3Hz, 10amp, 单相 200,220,240,260 VAC +/-10%, 50Hz +/- 3amp 单相</td></tr><tr><td>空气压力：</td><td>最低 60 psi (414Kpa, 4.2 kg/cm2)</td></tr><tr><td>方面：</td><td>宽：22 英寸（56 厘米），深：26 英寸（66 厘米），高：48 英寸（122 厘米）</td></tr><tr><td>重量：</td><td>净重 350 磅（159 公斤）</td></tr><tr><td>液晶触摸屏：</td><td>155mm x 85mm，分辨率 800 x 480</td></tr></tbody></table>',
            'type':'table'
        },{
            'content':'Faster. Better Control. Better Resolution.Custom Electronics that are matched to the instrument. Better control. Better resolution. Other RPAs use off-the-shelf PLCs to save money, but can’t fine-tune their electronics to their instrument – often overshoot set points then spend valuable time stabilizing.Efficient Die CoolingEfficient die cooling that gets your instrument ready for the next test. Why wait 20 minutes for dies to cool down when Premier instruments take about 6 minutes. (And our instruments are smart enough to know when the instrument reaches the right temperature. Others, not so much.Because they are designed specifically for Premier instruments, our heating control system ramps up heating cycles faster and maintains control for more accurate cure times and more efficient production.More accurate measurements. No loss of signal thanks to Premier’s Smart Alignment and Dynamic Symmetry. On-target, parallel die closing, high stiffness and constant closing force.Work smarter not harder with lighter, cast aluminum frames. Not only are Premier frames light, but incredibly stiff for less variability. What’s more, Premier instruments incorporate frame compliance into the calibration for better data.Our incredibly intuitive user interface comes to you through a large, bright, touch screen panel that lets you navigate to the view you want or the information you need, fast and easy.Okay… that’s a really small thing. But QA and R&D technicians love having a way to keep their workspace clear.)',
            'type':'text'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e6%80%bb%e7%90%86-mv/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    firstTypeName = 'Premier MDR'
    Description = [
        {
            'content':'如何将 Premier MV 与所有其他人进行比较。卓越的模具冷却和温度稳定性——得益于轻量模具和专有的数字温度控制，Premier MV 提供了出色的温度稳定性，与以前的型号相比，模具冷却时间减少了 45%。 你的粘度计能做到吗？多速测量– 控制多个剪切速率以建立幂律曲线和其他剪切粘度图。转子对齐检测——通过关闭未对齐的转子来防止对转子和轴的意外损坏，并减少更换转子和轴所需的时间和成本。自动静重校准——允许在几秒钟内校准仪器。高级验证程序——确保您满足 ASTM 规定的设定点。标准多区应力松弛和变速数字电机——对于获取高级处理信息（例如识别触变材料）至关重要。可选的长寿命 O 型圈– 通过减少频繁的清洁和校准，让您的仪器长时间工作。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Premier-MDR-2_900-852x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Premier-MDR-1_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Custom-electronics_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Advance-die-cooling_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Better-heating-control_Alpha-Tech_211130_0128_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Dynamic-Symmetry-alignment_900-200x300.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Cast-aluminum-frame_900-224x300.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Drawer_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha_MDR_Flyer_FA-1.pdf',
            ],
            'type':'img'
        },{
            'content':'<table>	<tbody>		<tr>			<td>频率：</td>			<td>100 cpm (1.67 赫兹)</td></tr>		<tr>		<td>温度范围：</td>			<td>环境温度为 446°F (230°C)</td>	</tr>		<tr>			<td>拉紧：</td>			<td>0.5 标准（7%）； 0.2、1.0、3.0 和 7.17 度</td>		</tr>		<tr>			<td></td>			<td>(2.8%、14%、42% 或 100%) 可用 ML、MH、MH-ML、Ts1、Ts2、</td>		</tr>		<tr>			<td>在船上：</td>			<td>T10、T50、T90、S？ 在 ML，S? 在 MH、TD 在 ML、TD 在 MH、最大固化速率、最大固化速率时间、压力点 PH-PL 和压力时间点</td>		</tr>		<tr><td>测试标准：</td>			<td>符合 ASTM D5289、ISO6502 和 DIN 53529</td>		</tr>		<tr>			<td>电气：</td>			<td>100/110/120/130 VAC+/- 10%, 60 +/- 3Hz, 10amp, 单相 200,220,240,260 VAC +/-10%, 50Hz +/- 3amp 单相</td>		</tr>		<tr>			<td>空气压力：</td>			<td>最低 60 psi (414Kpa, 4.2 kg/cm2)</td>		</tr>		<tr>			<td>方面：</td>			<td>宽：22 英寸（56 厘米），深：26 英寸（66 厘米），高：48 英寸（122 厘米）</td>		</tr>		<tr>			<td>重量：</td>			<td>净重 350 磅（159 公斤）</td>		</tr>		<tr>			<td>液晶触摸屏：</td>			<td>155mm x 85mm，分辨率 800 x 480</td>		</tr>	</tbody></table>',
            'type':'table'
        },{
            'content':'Faster. Better Control. Better Resolution.Custom Electronics that are matched to the instrument. Better control. Better resolution. Other RPAs use off-the-shelf PLCs to save money, but can’t fine-tune their electronics to their instrument – often overshoot set points then spend valuable time stabilizing.Efficient Die CoolingEfficient die cooling that gets your instrument ready for the next test. Why wait 20 minutes for dies to cool down when Premier instruments take about 6 minutes. (And our instruments are smart enough to know when the instrument reaches the right temperature. Others, not so much.)Custom Designed Heating Control SystemBecause they are designed specifically for Premier instruments, our heating control system ramps up heating cycles faster and maintains control for more accurate cure times and more efficient production.Dynamic Symmetry and Smart AlignmentMore accurate measurements. No loss of signal thanks to Premier’s Smart Alignment and Dynamic Symmetry. On-target, parallel die closing, high stiffness and constant closing force.Lighter. Stronger. Stiffer.Work smarter not harder with lighter, cast aluminum frames. Not only are Premier frames light, but incredibly stiff for less variability. What’s more, Premier instruments incorporate frame compliance into the calibration for better data.Control with a Personal TouchOur incredibly intuitive user interface comes to you through a large, bright, touch screen panel that lets you navigate to the view you want or the information you need, fast and easy.Storage DrawerOkay… that’s a really small thing. But QA and R&D technicians love having a way to keep their workspace clear.',
            'type':'text'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e9%ab%98%e7%ba%a7-esr/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    firstTypeName = 'Premier ESR'
    Description = [
        {
            'content':'如何将 Premier ESR 与所有其他人进行比较。实际上，这比您想象的要难。 虽然许多公司提供昂贵、技术复杂且测试时间过高的 DMA 仪器，但 Alpha Technologies 还是推出了 Premier ESR。 Alpha 的 Premier ESR 符合 ASTM D7750。 它提供了一种在任何必要的固化周期下固化复合材料的经济有效的方法。 此外，ESR 能够根据这些条件测量凝胶、固化和最终物理特性。（顺便说一下，为了享受一点轻松的阅读乐趣，请查看 Alpha 的流变学研究员 H. Pawlowski 撰写的“使用封装样品流变仪改进预浸料粘度、凝胶和固化的测量” ，可通过 SAMPE 北美 2017 年会议在西雅图获得。 )也就是说，Premier ESR 带有许多标准功能，当您考虑购买 ESR 时，这些功能很重要。精密封装的样品几何形状——样品的加压将样品固定在适当的位置。 这反过来又允许测量单向层压板以及优化固化曲线在真等温条件下测试——对于确定固化状态和最佳粘度很重要，因为许多反应是高度放热的，需要精确的温度控制。独立的触摸屏用户界面——用于仪器管理的工作台和用于数据分析的在线管理器。 我们的定制电子设备为您提供真正的多任务处理。 与其他人使用的缓慢 PLC 不同，无需等待测试完成即可查看数据。软关闭操作——Premier ESR 控制压板的压力，以保持样品定位。定制设计的扁平模具——替代 Premier RPA 的双锥模具。 我们的扁平模具对于测试非常坚硬的材料至关重要。K 因子校准– 通过考虑传感器的合规性，将范围扩展到更高的模量值。 允许在固化后测量非常高模量的材料。获得专利的 O 形圈– 提供恒定的树脂纤维比并提高可重复性。获得专利的限滑模具选项——专为热塑性塑料测试而设计符合 ASTM D7750 – 该标准于 2013 年推出，根据粘弹性特性定义了固化和固化时间的测量，适用于树脂和预浸料。高温测试——Premier ESR 将测试范围从我们的标准 230ºC 扩展到 350ºC。除了将测试范围从 30ºC 扩展到 350ºC 之外，Premier ESR 的测试条件范围还包括：扭矩 – 从 0.005º (O.o7%) 到 90º (1256%)频率 – 0.0016 Hz 至 50 Hz时间 – 0.1 分钟至 9999.99 分钟',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Premier-ESR_Alpha-Tech_220127_4343_900-752x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Premier-ESR_Alpha-Tech_220127_4349_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Custom-electronics_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Advance-die-cooling_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Better-heating-control_Alpha-Tech_211130_0128_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Dynamic-Symmetry-alignment_900-200x300.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Cast-aluminum-frame_900-224x300.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Drawer_900-300x200.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-Premier-ESR-Brochure.pdf',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-Premier-ESR-Declaration-of-Conformity-CE-Certification.pdf'
            ],
            'type':'img'
        },{
            'content':'<table>	<tbody>		<tr>			<td>升温速率：</td>			<td>0.36°F/分钟。 （0.20 °C/分钟）至 90 °F/分钟。 (50°C/分钟)</td>		</tr>		<tr>			<td>最大冷却速度：</td>			<td>54°F/分钟。 （30°C/分钟）</td>		</tr>		<tr>			<td>测量：</td>			<td>扭矩 (S’, S”, S*), Tan(Delta), 动态粘度 (η’, η”, η*), 剪切模量 (G’, G”, G*), 温度（°C 或 °F ), 应变 (度, %, 分数应变), 频率 (cpm, Hz, 弧度/秒), 压力 (kPa, psi)</td>		</tr>		<tr>			<td>电气：</td>			<td>100/110/120/130 VAC ±10%, 60 ±3 Hz, 20 amp 单相 <br>200/220/240/260 VAC ±10%，50 ±3 Hz，10amp 单相</td>	</tr>		<tr>			<td>空气压力：</td>			<td>80 psi (5.6 kg/cm) 最小 2551 kPa</td>		</tr>		<tr>			<td>方面：</td>			<td>宽：22 英寸（56 厘米），高：48 英寸（122 厘米），深：25 英寸（64 厘米）</td>		</tr>		<tr>			<td>重量：</td>			<td>净重 346 磅（157 公斤），总重 616 磅（280 公斤）</td>		</tr>	<tr>			<td>样品腔：</td>			<td>3.5 厘米</td>		</tr>		<tr>			<td>样品尺寸：</td>			<td>直径 41 毫米，标称厚度 2.6 毫米</td>		</tr>		<tr>			<td>温度范围：</td>			<td>环境温度至 662°F (350°C)</td>		</tr></tbody></table>',
            'type':'text'
        },{
            'content':'Faster. Better Control. Better Resolution.Custom Electronics that are matched to the instrument. Better control. Better resolution. Other RPAs use off-the-shelf PLCs to save money, but can’t fine-tune their electronics to their instrument – often overshoot set points then spend valuable time stabilizing.Efficient Die CoolingEfficient die cooling that gets your instrument ready for the next test. Why wait 20 minutes for dies to cool down when Premier instruments take about 6 minutes. (And our instruments are smart enough to know when the instrument reaches the right temperature. Others, not so much.)Custom Designed Heating Control SystemBecause they are designed specifically for Premier instruments, our heating control system ramps up heating cycles faster and maintains control for more accurate cure times and more efficient production.Dynamic Symmetry and Smart AlignmentMore accurate measurements. No loss of signal thanks to Premier’s Smart Alignment and Dynamic Symmetry. On-target, parallel die closing, high stiffness and constant closing force.Lighter. Stronger. Stiffer.Work smarter not harder with lighter, cast aluminum frames. Not only are Premier frames light, but incredibly stiff for less variability. What’s more, Premier instruments incorporate frame compliance into the calibration for better data.Control with a Personal TouchOur incredibly intuitive user interface comes to you through a large, bright, touch screen panel that lets you navigate to the view you want or the information you need, fast and easy.Storage DrawerOkay… that’s a really small thing. But QA and R&D technicians love having a way to keep their workspace clear.',
            'type':'text'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/alphaview-dispergrader/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    table_str = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8271"]/table')[0],encoding='utf-8',method='html').decode()
    firstTypeName = 'AlphaView Dispergrader'
    Description = [
        {
            'content':'现在，再仔细看看。AlphaView Dispergrader 有两种型号以满足您的特定需求。 标准分辨率模型可以分辨低至 3 微米的颗粒。 我们的高分辨率模型能够分辨小至 1 微米的颗粒。两种型号都使用带 FireWire 连接 (USB?) 的彩色相机。用于执行分析的颜色通道以及相机曝光时间都是用户可选择的，允许操作员分析不同颜色的化合物。照明由 LED 阵列提供。 照明方向是用户可选择的。 所有照明方向的入射角均为 30º，符合 ISO 11345 和 ASTM D7723 的要求。直观的控制。 企业软件。 定制报告。ShuttleXpress 软件预装在计算机上，用于控制样品平移和聚焦步进电机。 或者，操作员可以使用 Workbench 测试显示中的仪表板控制面板来控制仪器。一旦测试开始，实时图像就会被捕获并通过图像算法进行处理，以抑制样品表面的噪声和不规则性。 然后对图像进行过滤和阈值处理，以生成用于计算的黑白图像。Alpha 的专有企业软件处理、显示和分析数字化图像，以便与您自己建立的参考比例进行视觉比较，或与标准参考图像和分类进行自动比较。 软件中预装了参考标准和刻度，例如 Phillips 10 度刻度。 软件中显示的直方图用于排列团块的数量和大小。快速、简单且具有成本效益。虽然有三种分散测试方法——电气、机械和光学——但电气不再可行，因为二氧化硅等填料不被认为是导电的。 需要与每个复合配方建立机械方法相关性。 在光学测试的两个选项中，透射光耗时且需要复杂的样品制备。 AlphaView Dispergrader 采用反射光法，快速、简单且具有成本效益。半自动化操作使您可以非常快速地检查样品。扫描可以是自动或手动的。精密步进电机和导轨用于移动光学平台，允许操作员通过一次样品放置获取多个读数。我们的重新测试单个点选项意味着如果出现问题，您可以重新测试一个点，而不必重新开始测试。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Dispergrader_Alpha-Tech_211229_3008_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Dispergrader_Alpha-Tech_211229_3009_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Histogram_K-DG3.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Dispergrader_Alpha-Tech_211229_3006_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-DisperGrader-Brochure.pdf',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-DisperGrader-Declaration-of-Conformity-CE-Certification.pdf'
            ],
            'type':'img'
        },{
            'content':table_str,
            'type':'table'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/at10-%e9%80%9a%e7%94%a8/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    table_str = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8271"]/table')[0],encoding='utf-8',method='html').decode()
    firstTypeName = 'AT10'
    Description = [
        {
            'content':'Universal 不仅仅意味着拉力测试仪。Alpha 的 AT10 是一款易于使用的台式万能拉伸试验机，最大负载值为 10kN。 它允许您确定材料在各种条件下的强度，并测量材料可以承受的最大载荷。 可选的测厚仪提供有关受拉材料的附加数据点和信息。AT10 的质量和研发实验室测试组合包括：拉伸压缩弯曲剥眼泪剪切摩擦刺O形圈合适的测试人员。 与之配套的正确软件。AT10 是一款全面的计算机控制测试仪器，具有全方位的用户功能，包括数据点选择器和自定义数据点计算器。 Alpha 的高级企业软件套件可以轻松重新计算结果，以便在运行测试后添加额外的数据点。 数据可以存储在仪器的计算机上或与 Enterprise LIMS 平台连接。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/AT10-Alpha-Tech_211229_3171_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/AT10-Alpha-Tech_211229_3234_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/AT10-Alpha-Tech_211229_3168_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/07/AT10-Grip-Catalog-Rev06.pdf',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/AT10_Universall-Flyer_LO1.pdf'
            ],
            'type':'img'
        },{
            'content':table_str,
            'type':'table'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/d2020%e7%b3%bb%e5%88%97/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    table_str = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8271"]/table')[0],encoding='utf-8',method='html').decode()
    table_str2 = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-2091"]/table')[0],encoding='utf-8',method='html').decode()
    firstTypeName = 'D2020 密度仪'
    Description = [
        {
            'content':'Alpha 的 D2020 仪器可为多达 20 个样品提供全自动测试。 它们提供简单但精确的解决方案来确定材料是否适合您的应用。 大多数竞争对手将他们的单一测试操作自动化，但需要操作员加载样品、运行测试、取出样品、重复。 相比之下，Alpha 的 D2020 自动 20 个样品盒有助于确保可重复性，同时让操作员腾出时间来完成实验室中的其他任务。D2020 密度尤里卡！ Alpha 的 D2020 密度仪基于阿基米德原理，其中施加在浸入水中的测试样品上的向上浮力等于样品在向上方向置换和作用的水的重量。D2020 密度利用化合物在空气和水中的重量来考虑测试期间的任何环境差异，从而提高质量标准和精度。全自动操作有助于确保可重复性，同时让操作员可以在实验室中完成其他任务。 此外，快速读数有助于减少吸水率，从而转化为更准确的读数。 为了获得更高的精度，液体的比重会自动根据温度进行校正。D2020 硬度Alpha 的 Shore A 和 IRHD 仪器基于 Albert F. Shore 在 1920 年代开发的用于测量材料硬度的测试方法。 这种方法是衡量给定材料对永久压痕的抵抗力的量度 – 即用特定力在材料上产生的压痕深度的量度。 两种版本都对橡胶和聚合物零件提供高度可重复的测量。ISO 48 中定义的国际橡胶硬度 (IRHD) 是欧洲首选的全自动测量程序。 IRHD 硬度值直接从 Alpha 企业软件的内部查找表中读取。肖氏 A 法（根据 ASTM D2240 定义）允许测量初始硬度或给定时间后的压痕硬度。除了 20 个样品的自动化盒外，D2020 硬度计还可以自动旋转，允许每个测试样品进行多个读数。一流的仪器值得拥有世界一流的软件。D2020 仪器使用 Alpha 的专有企业软件套件（包括 Pathfinder Workbench 和 Labjack 软件）运行，将密度和硬度测试连接到您的 LIMS。 创建数据后，企业软件将数据组织成报告，并可以执行分析，使用户能够统计控制他们的制造过程。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/D2020-Density_Alpha-Tech_211229_3079_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/D2020-Hardness_Alpha-Tech_211229_3063_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/D2020-Hardness_Alpha-Tech_211229_3057_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/D2020-Density_Alpha-Tech_211229_3084_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-D2020-Density-Brochure.pdf',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Alpha-D2020-Hardness-Brochure.pdf',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Alpha-D2020-Density-Declaration-of-Conformity-CE-Certification.pdf',
            ],
            'type':'img'
        },{
            'content':table_str,
            'type':'table'
        },{
            'content':table_str2,
            'type':'table'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e6%a0%b7%e5%93%81%e8%87%aa%e5%8a%a8%e5%8c%96%e7%b3%bb%e7%bb%9f/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    table_str = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8271"]/table')[0],encoding='utf-8',method='html').decode()
    table_str2 = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8272"]/table')[0],encoding='utf-8',method='html').decode()
    table_str3 = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8273"]/table')[0],encoding='utf-8',method='html').decode()
    firstTypeName = '样品自动化系统'
    Description = [
        {
            'content':'专为您的 Alpha Premier 仪器设计的自动化系统。从一次加载一个样品到排队 224 个样品进行通宵测试，Alpha Technologies 提供了一系列样品自动化选项，可满足您的测试需求。 Alpha 紧凑、轻便的样品处理选项专为快速、可靠和易于操作的处理而设计。 所有样品处理选项都与 Premier MDR 和 Premier RPA 系列仪器无缝集成，以便快速轻松地进行改装。Premier 5 Queue 和 10 Queue – 手动装载 5-10 个方形、圆形或不规则尺寸的样品。Premier 3D – Carrousel 装载系统，可容纳多达 36 个可互换的样品载体。 3D 单元的简单设计以实惠的价格提供中等容量的排队选项。Premier 高容量– 装载和去托盘装载系统，一次最多可排队 224 个样品。 高容量选项是全球最快的样品处理单元。所有样品处理选项都可以使用 2、3 或 4 个胶卷，并且 Alpha Technologies 拥有超过 25 种不同的胶卷选项，可为任何应用提供合适的胶卷。Sample Automation on a Premier RPA',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Sample-Automation_Alpha-Tech_211130_0220_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Sample-Automation_Alpha-Tech_211229_3193_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Sample-Automation_Alpha-Tech_211229_3047_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Sample-Automation_Alpha-Tech_211130_0169_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Sample-Automation_Alpha-Tech_211130_0209_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Alpha_Sample-Auto_LO3.pdf',
            ],
            'type':'img'
        },{
            'content':table_str,
            'type':'table'
        },{
            'content':table_str2,
            'type':'table'
        },{
            'content':table_str3,
            'type':'table'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e6%a0%b7%e5%93%81%e5%88%87%e5%89%b2%e5%99%a8/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    table_str = etree.tostring(tree.xpath('//*[@id="elementor-tab-content-8271"]/table')[0],encoding='utf-8',method='html').decode()
    firstTypeName = '样品切割器'
    Description = [
        {
            'content':'定容样品切割……每个样品，每次。坏样本可能是测试环境中最可避免的错误来源。 每次测试的样本量和形状不一致可能会给您的结果带来不必要的变化。 这是因为扭矩受模具距离或距离的影响——体积的变化会变成数据的变化。 Alpha 经行业验证的定容样品切割器提供两种简单的解决方案来确保样品相同——一种用于流变仪，一种用于门尼粘度计。 精确、准确的样品制备意味着您的数据更可靠。 这提高了您设定更严格规格和交付卓越最终产品的能力。Alpha 的样品切割器可在几秒钟内生产出恒定体积的橡胶样品。 对于流变仪和粘度计测试的可重复性至关重要的 MDR、RPA 和 MV 仪器，定容样品是理想的选择。 有两种样品切割器可供选择，样品可以完美地放入相应的样品托盘中。双作用气动样品压机——在几秒钟内获得橡胶样品。紧凑的尺寸– 非常适合有效利用工作台空间和仪器放置。双手安全触摸开关——利用光学传感器，需要两只手来激活机器。 这提高了操作员的安全性，并且不需要防护罩。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3106_900-811x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3090_900-811x1024.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3101_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/03/Sample-Cutter_Alpha-Tech_211229_3091_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/Alpha-Sample-Cutter-Brochure.pdf',
            ],
            'type':'img'
        },{
            'content':table_str,
            'type':'table'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    url = 'https://www.alpha-technologies.com/zh-hans/instruments/%e6%ac%a1%e9%9b%b6%e6%8a%80%e6%9c%af/'
    resp = requests.get(url=url,headers=headers)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)
    table_str = etree.tostring(tree.xpath('//*[@id="content"]/div/section[5]/div/div/div/section/div/div/div/div[2]/div/table')[0],encoding='utf-8',method='html').decode()
    firstTypeName = '次零技术'
    Description = [
        {
            'content':'对关键轮胎性能预测指标的更快测试。现在可以在扭转时进行轮胎性能预测器测量——在大约 23 分钟内提供 11 个关键轮胎性能预测器。 因此，您无需在 DMA 上花费大量资金、聘请熟练的技术人员并等待很长时间才能获得结果，而是可以将 Sub-Zero 技术添加到您的 Premier RPA 中，并以一种高效、低成本的方式获取您想要的数据-有效的工具。Alpha 的科学家和工程师将干燥器、冷却器（不使用液氮）和专有技术相结合，以测试低至 -25ºC 的固化样品。 此外，这些测试条件可以包含在标准 RPA 发布测试的末尾，用于测量未固化的加工、固化/焦烧和物理性能。 您可以使用 Alpha 的 Sub-Zero 技术添加以前专属于 DMA 的滚动阻力和湿/冰牵引力和其他预测指标的测试。一个测试，一个样本，使用一个非常酷（双关语）的仪器。 Alpha 的 Sub-Zero 技术消除了低温质量测试的障碍。',
            'type':'text'
        },{
            'content':[
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/SubZero_Alpha-Tech_211130_0181_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/SubZero_Alpha-Tech_211229_3230_900.jpg',
                'https://www.alpha-technologies.com/wp-content/uploads/2022/04/SubZero_Alpha-Tech_211229_3224_900-776x1024.jpg',
            ],
            'type':'img'
        },{
            'content':table_str,
            'type':'table'
        }
    ]
    solu_dic = {}
    solu_dic['FirstType'] = ''
    solu_dic['SecondType'] = ''
    solu_dic['SolutionUrl'] = url
    solu_dic['SolutionHTML'] = resp.text.strip()
    solu_dic['SolutionJSON'] = ''
    solu_dic['SolutionName'] = firstTypeName
    solu_dic[firstTypeName] = Description
    solu_dic['ProductUrl'] = []
    final_dic['pro'].append(solu_dic)
    logger.info(f'爬取应用方案{len(final_dic["pro"])}/10条数据')

    return final_dic

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic = get_solution(headers)
    filename,dic = f'阿尔法解决方案{len(final_dic["pro"])}.json',final_dic
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    print(f'爬取{len(final_dic["pro"])}条方案，存储在{filename}中.')