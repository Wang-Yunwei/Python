# -*- coding:utf-8 -*-
import logging
import os

import PIL

from BASEUtile import MINIO

log_path = os.path.dirname(os.getcwd())
print(log_path)
class LoggerColl:
    def __init__(self,loggername):
        #创建一个logger
        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(logging.INFO)
        #创建一个handler，用于写入日志文件

        #self.logname = 'D://out1.log'
        self.logname = "/home/wkzn/JIKUPI/out1.log"  # 正常使用
        #self.logname = "D:\\01机库代码整理6-12\\集成版本开发中\\SVN版本（含大流程）\\00_source\\JIKUPI\\out.log"
        #logname = os.getcwd()+'/out.log' #指定输出的日志文件名
        #检测文件是否存在，如果不存在则创建一个文件
        #创建文件
        if not os.path.exists(self.logname):
           with open(self.logname,'w') as f:
               pass

        fh = logging.FileHandler(self.logname,encoding = 'utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
        fh.setLevel(logging.DEBUG)

        #创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_log(self):
        '''
        定义一个函数，回调logger实例
        '''
        return self.logger
    def delete_log(self):
        '''
        删除日志文件并创建一个新文件
        :return:
        '''
        if os.path.exists(self.logname):  # 如果文件存在
            # 删除文件
            os.remove(self.logname)
            # 创建一个logger
            self.logger = logging.getLogger(self.logname)
            self.logger.setLevel(logging.INFO)
            # 创建一个handler，用于写入日志文件

            # logname = '/home/pi/JIKUPI/out.log'
            #self.logname = "/home/wkzn/JIKUPI/out.log"  # 正常使用
            # logname = os.getcwd()+'/out.log' #指定输出的日志文件名
            # 检测文件是否存在，如果不存在则创建一个文件
            # 创建文件
            if not os.path.exists(self.logname):
                with open(self.logname, 'w') as f:
                    pass
            fh = logging.FileHandler(self.logname, encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
            fh.setLevel(logging.DEBUG)
            # 创建一个handler，用于将日志输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # 定义handler的输出格式
            formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            # 给logger添加handler
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
    def upload_log(self):
        utilminio = MINIO.MiniUtils(self.logger)
        utilminio.start_uploadlog()


if __name__ == '__main__':
    #t = Logger("hmk").get_log().debug("User %s is loging" % 'jeck')
    print(PIL.__version__)