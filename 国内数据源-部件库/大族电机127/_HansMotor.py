from ACServoMotor import *
from ServoModulePlatform import *
from TorqueMotor import *
from ARCMotor import *
from DCMotor import *
from DirectDriveMotor import *


if __name__ == '__main__':
    final_dic = {'pro':[]}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'    
    }
    final_dic['pro'] += AC_Servo_Motor(headers=headers,filename='交流伺服电机.json',typeName='交流伺服电机')
    final_dic['pro'] += ServoModule(headers=headers,filename='伺服模组平台.json',typeName='伺服模组平台')
    final_dic['pro'] += TorquMotor(headers=headers,filename='力矩电机.json',typeName='力矩电机')
    final_dic['pro'] += ARC_Motor(headers=headers,filename='弧形管形音圈电机.json',typeName='弧形管形音圈电机')
    final_dic['pro'] += Linear_Motor(headers=headers,filename='直线电机.json',typeName='直线电机')
    final_dic['pro'] += DirectDriveMotor(headers=headers,filename='直驱电机.json',use_proxies=False,typeName='直驱电机')
    
    filename = f'大族电机{len(final_dic["pro"])}.json'
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_dic, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
    logger.info(f"爬取{len(final_dic['pro'])}条数据完成，存储在{filename}中.")



