# -*- coding: utf-8 -*- 
# @Time : 2023/8/25 9:59 
# @Author : ZKL 
# @File : ActivateUtils.py
import uuid
import datetime
from Activate.ASHelper import get_aes
import hashlib
# import fcntl#只有linux下才可以使用
import socket, struct

# from ConfigIni import ConfigIni
import BASEUtile.Config as Config

class ActivateUtils(object):
    def __init__(self, log):
        self.maccode = ""
        self.config = Config
        self.log = log

    def getMacCode(self):
        '''
        获取机器码，机器mac地址
        '''
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    def getMacCode1(self, eth_name):
        # s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        # info=fcntl.ioctl(s.fileno(),0x8927,struct.pack('256s',eth_name[:15]))
        # return ":".join(['%02x' % ord(char) for char in info[18:24]])
        pass

    def get_left_days(self, lic_date):
        '''
        计算激活码剩余天数
        '''
        current_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        current_time_array = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        lic_date_array = datetime.datetime.strptime(lic_date, "%Y-%m-%d %H:%M:%S")
        remain_days = lic_date_array - current_time_array
        remain_days = remain_days.days
        if remain_days < 0:
            return -1
        else:
            return remain_days
    def get_pass_date(self):
        '''
        获取过期日期
        '''
        license_dic = self.read_license(self.config.get_license_code())
        lic_date_array = datetime.datetime.strptime(license_dic['time_str'], "%Y-%m-%d %H:%M:%S")
        return lic_date_array

    def hash_msg(self, msg):
        '''
        计算一个字符串的hascode
        '''
        sha256 = hashlib.sha256()
        sha256.update(msg.encode('utf-8'))
        res = sha256.hexdigest()
        return res

    def read_license(self, license_result):
        '''
        读取激活码
        '''
        lic_msg = bytes(license_result, encoding="utf8")
        license_str = get_aes().decrypt(lic_msg)
        license_dic = eval(license_str)
        return license_dic  # 字典

    def check_license_date(self, lic_date):
        '''
        确定激活码的时效
        '''
        current_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        current_time_array = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        lic_date_array = datetime.datetime.strptime(lic_date, "%Y-%m-%d %H:%M:%S")
        remain_days = lic_date_array - current_time_array
        remain_seconds = remain_days.seconds
        remain_days = remain_days.days
        if remain_days < 0:
            return False
        elif remain_days == 0 and (remain_seconds < 0 or remain_seconds == 0):
            return False
        else:
            return True

    def checktime(self, lic_date):
        # str_eval1="datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')"
        str_eval1 = "datetime.datetime.strptime( datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')"
        lic_date_array = "datetime.datetime.strptime(lic_date, '%Y-%m-%d %H:%M:%S')"
        remain_days = eval(lic_date_array) - eval(str_eval1)
        remain_seconds = remain_days.seconds
        remain_days = remain_days.days

        print(f"{remain_days}")
        return eval(str_eval1)

    def check_license_psw(self, psw):
        '''
        确定机器码是否匹配
        '''
        mac_addr = self.get_unique_identifier()
        hashed_msg = self.hash_msg('zyhk_wkzn' + str(mac_addr))
        if psw == hashed_msg or psw == "":
            return True
        else:
            return False

    def checkLicens(self):
        res = {}
        try:
            license_dic = self.read_license(self.config.get_license_code())
            date_bool = self.check_license_date(license_dic['time_str'])
            psw_bool = self.check_license_psw(license_dic['psw'])
            if psw_bool:
                if date_bool:
                    res['status'] = True
                    res['time'] = license_dic['time_str']
                    res['msg'] = "一切正常"
                else:
                    res['status'] = False
                    res['time'] = license_dic['time_str']
                    res['msg'] = "激活码过期"
                    self.log.get_log().info(res)
            else:
                res['status'] = False
                res['time'] = license_dic['time_str']
                res['msg'] = "MAC不匹配, License无效, 请更换License"
                self.log.get_log().info(res)
        except Exception as ex:
            res['status'] = False
            res['time'] = ''
            res['msg'] = "激活码无效"
            self.log.get_log().info(res)
        return res

    def checkInputLicense(self, input_license_code):
    # 判定输入的license是否有效
        res = {}
        try:
            license_dic = self.read_license(input_license_code)
            date_bool = self.check_license_date(license_dic['time_str'])
            psw_bool = self.check_license_psw(license_dic['psw'])
            if psw_bool:
                if date_bool:
                    res['status'] = True
                    res['time'] = license_dic['time_str']
                    res['msg'] = "一切正常"
                else:
                    res['status'] = False
                    res['time'] = license_dic['time_str']
                    res['msg'] = "输入的激活码过期"
                    self.log.get_log().info(res)
            else:
                res['status'] = False
                res['time'] = license_dic['time_str']
                res['msg'] = "输入的MAC不匹配, License无效, 请更换License"
                self.log.get_log().info(res)
        except Exception as ex:
            res['status'] = False
            res['time'] = ''
            res['msg'] = "输入激活码无效"
            self.log.get_log().info(res)
        return res

    def get_mac_address(self):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
        print(f"MAC Address: {mac}")
        return mac

    def get_unique_identifier(self):
        node = uuid.getnode()
        if node == 0x000000000000:
            node = uuid.uuid1().node
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(node))
        return str(unique_id)

if __name__ == "__main__":
    # configini=ConfigIni()
    # activate = ActivateUtils(configini, None)
    # print(activate.get_pass_date())
    # print(activate.get_unique_identifier())
    pass
