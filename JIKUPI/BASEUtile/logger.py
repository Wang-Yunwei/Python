# -*- coding:utf-8 -*-
import datetime
import logging
import os
import time
from logging import handlers

import PIL

from BASEUtile import MINIO

class Logger:
    def __init__(self,loggername):
        #创建一个logger
        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(logging.INFO)
        #创建一个handler，用于写入日志文件
        #self.basicDir="D://log"
        self.basicDir = "/home/wkzn/JIKUPI/log"  # 正常使用
        if not os.path.exists(self.basicDir):
            os.makedirs(self.basicDir)
        self.logname = f"{self.basicDir}/log_{ datetime.date.today()}.txt"
        self.day_handler=handlers.TimedRotatingFileHandler(filename=self.logname,when="D",backupCount=10,encoding='utf-8')
        #创建一个handler，用于将日志输出到控制台
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        self.formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        #fh.setFormatter(formatter)
        self.ch.setFormatter(self.formatter)
        self.day_handler.setFormatter(self.formatter)
        # 给logger添加handler
        #self.logger.addHandler(fh)
        self.logger.addHandler(self.ch)
        self.logger.addHandler(self.day_handler)

    def get_log(self):
        '''
        定义一个函数，回调logger实例
        '''
        newloggername=f"{self.basicDir}/log_{ datetime.date.today()}.txt"
        if os.path.exists(newloggername):
           #日志文件已经存在
            return self.logger
        else:#日志文件不存在
            print("创建新日志文件")
            self.logger.removeHandler(self.day_handler)
            #self.logger.removeHandler(self.ch)
            self.logname=newloggername
            self.day_handler = handlers.TimedRotatingFileHandler(filename=self.logname, when="D", backupCount=10,
                                                                 encoding='utf-8')
            self.day_handler.setFormatter(self.formatter)
            #self.logger.addHandler(self.ch)
            self.logger.addHandler(self.day_handler)

        return self.logger
    def delete_log(self):
        '''
        删除日志文件并创建一个新文件
        :return:
        '''
        if os.path.exists(self.basicDir):  # 如果文件存在
            try:
                # 删除文件,删除30天之前的日志文件
                starttime = (datetime.datetime.today() - datetime.timedelta(days=1000)).strftime("%Y-%m-%d")
                endtime = (datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                filelist = self.getLogFiles(starttime, endtime)
                for file in filelist:
                    os.remove(file)
            except Exception as ex:
                self.logger.info(f"删除日志失败,{ex}")
        else:
            os.remove("/home/wkzn/JIKUPI/out.log")

    def upload_log(self):
        utilminio = MINIO.MiniUtils(self)
        utilminio.start_uploadlog()

    def getLogFiles(self,starttime,endtime):
        '''
        根据起止时间获取时间范围内所有的文件列表
        2014-01-15
        2024-01-20
        '''
        filelist=[]
        #获取目录下文件列表
        for file in os.listdir(self.basicDir):
            #每个文件操作,file为每个文件的名字
            #分析每个文件名字的时间
            filename_time=file.split(".")[0].split("_")[-1]
            if self.is_time_in_range(starttime,endtime,filename_time):
                filelist.append(self.basicDir+"//"+file)
        return filelist

    def is_time_in_range(self,starttime,endtime,target_time):
        start=datetime.datetime.strptime(starttime,"%Y-%m-%d")
        end=datetime.datetime.strptime(endtime,"%Y-%m-%d")
        target=datetime.datetime.strptime(target_time,"%Y-%m-%d")

        if start<=target<=end:
            return True
        else:
            return False


if __name__ == '__main__':
    #t = Logger("hmk").get_log().debug("User %s is loging" % 'jeck')
    log=Logger("")
    # num=0
    # while num<10:
    #     log.get_log().info(f"日志信息")
    #     time.sleep(5)
    #     num+=1
    # log.delete_log()
    #print(log.getLogFiles("2024-01-30","2024-01-31"))
    log.upload_log()
    #print(PIL.__version__)