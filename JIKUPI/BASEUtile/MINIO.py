'''
文件服务操作
'''

# !/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import threading

import minio

from BASEUtile.Config import Config

"""
@author:ZKL
@file:MinioObjectBase.py
@time:2021/12/04
"""
import os
class MiniUtils:

    def __init__(self,logger):
        self.minio_conf = {
            'endpoint': '124.70.41.186:9000',
            'access_key': 'admin',
            'secret_key': '1qaz@WSX',
            'secure': False
        }
        self.minioClient = minio.Minio(**self.minio_conf)
        self.logger=logger
        # self.basicDir="D://log"
        # self.loggerpath = "D://out.log"
        self.basicDir="/home/wkzn/JIKUPI"
        self.loggerpath="/home/wkzn/JIKUPI/out.log"
        #self.loggerpath = "/home/pi/JIKUPI/out.log"
        # if sys.platform=="linux":
        #     self.loggerpath = "/home/wkzn/JIKUPI/out.log"  # 正常使用
    # 从桶中下载一个对象txt、csv文件都可以
    def load_object(self,buck_name,object_name,localfilepath):
        try:
            data = self.minioClient.get_object(buck_name, object_name)
            with open(localfilepath, 'wb') as file_data:
                for d in data.stream(32 * 1024):
                    file_data.write(d)
        except Exception as err:
            self.logger.get_log().error(err)

    # 下载一个对象的指定区间的字节数组
    def load_partial_object(self,buck_name,object_name,localfilepath):
        try:
            data = self.minioClient.get_partial_object(buck_name, object_name, 2, 8)
            with open(localfilepath, 'wb') as file_data:
                for d in data:
                    file_data.write(d)
            #print("Sussess")  # 部分出现乱码
        except Exception as err:
            self.logger.get_log().error(err)

    # 下载并将文件保存到本地
    def fget_object(self,buck_name,object_name,localfilepath):
        try:
            print(self.minioClient.fget_object(buck_name, object_name, localfilepath))
        except Exception as err:
            self.logger.get_log().error(err)

    # 拷贝对象存储服务上的源对象到一个新对象
    # 注：该API支持的最大文件大小是5GB
    # 可通过copy_conditions参数设置copy条件
    # 经测试copy复制28M的文件需要663ms; 1.8G的压缩包需要53s
    def get_copy_object(self,buck_name,object_name,localfilepath):
        try:
            copy_result = self.minioClient.copy_object(buck_name, object_name,localfilepath)
            #print(copy_result)
        except Exception as err:
            self.logger.get_log().error(err)


    # 添加一个新的对象到对象存储服务
    """
    单个对象的最大大小限制在5TB。put_object在对象大于5MiB时，自动使用multiple parts方式上传。
    这样，当上传失败时，客户端只需要上传未成功的部分即可（类似断点上传）。
    上传的对象使用MD5SUM签名进行完整性验证。
    """

    def upload_object(self,buck_name,object_name,localfilename):

        # 放一个文件'application/csv'
        try:
            with open(localfilename, 'rb') as file_data:
                file_stat = os.stat(localfilename)
                self.minioClient.put_object(buck_name, object_name, file_data,
                                       file_stat.st_size)
            #print("Sussess")
        except Exception as err:
            self.logger.get_log().error(err)


    # 通过文件上传到对象中
    def fput_object(self,buck_name,object_name,localfilepath):
        try:
            print(self.minioClient.fput_object(buck_name, object_name,localfilepath))
            #print("Sussess")
        except Exception as err:
            self.logger.get_log().error(err)


    # 获取对象的元数据
    def stat_object(self,buck_name,object_name):
        try:
            print(self.minioClient.stat_object(buck_name, object_name))
        except Exception as err:
            self.logger.get_log().error(err)


    # 删除对象
    def remove_object(self,buck_name,object_name):
        try:
            self.minioClient.remove_object(buck_name, object_name)
        except Exception as err:
            self.logger.get_log().error(err)

    # 删除存储桶中的多个对象
    def remove_objects(self,buck_name,object_name):
        try:
            objects_to_delete = object_name  #列表
            for del_err in self.minioClient.remove_objects(buck_name, objects_to_delete):
                self.logger.get_log().info("Deletion Error: {}".format(del_err))

        except Exception as err:
            self.logger.get_log().error(err)


    # 删除一个未完整上传的对象
    def remove_incomplete_upload(self,buck_name,object_name):
        try:
            self.minioClient.remove_incomplete_upload(buck_name, object_name)
            #print("Sussess")
        except Exception as err:
            self.logger.get_log().error(err)
    #每次启动一个线程去执行这个任务，上传图片到minIo服务器
    def upload_img(self,buckname,file_object):#最后一个是图片的内容
        try:
            curPath =self.loggerpath
            if self.minioClient.bucket_exists(bucket_name=buckname):  # bucket_exists：检查桶是否存在
                pass
            else:
                self.minioClient.make_bucket(buckname)
            self.upload_object(buckname,file_object, curPath)
        except Exception as ex:
            # 删除当前文件
            print(ex)

    #启动一个线程任务
    def start_uploadfile(self,buckname,file_object):
        #threading.Thread(target=upload_img,args=(buckname,file_object,m0,m1)).start()
        threading.Thread(target=self.upload_img, args=(buckname, file_object)).start()

    # 每次启动一个线程去执行这个任务，上传日志到minIo服务器
    def upload_log(self):
        try:
            config = Config()
            configinfo_list = config.get_minio_config()
            minio_ip = configinfo_list[0][1]
            minio_username = configinfo_list[0][2]
            minio_password = configinfo_list[0][3]
            buckname = configinfo_list[0][4]
            self.minio_conf = {
                'endpoint': minio_ip,
                'access_key': minio_username,
                'secret_key': minio_password,
                'secure': False
            }
            self.minioClient = minio.Minio(**self.minio_conf)
            configinfo_list = config.getconfiginfo()
            station_id = configinfo_list[0][3]
            curPath = self.loggerpath
            if self.minioClient.bucket_exists(bucket_name=buckname):  # bucket_exists：检查桶是否存在
                pass
            else:
                self.minioClient.make_bucket(buckname)
            if station_id=="":
                station_id="out"
            #如果存在log文件夹，遍历log文件夹下的所有文件并上传
            if os.path.exists(self.basicDir):
                starttime= (datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
                endtime=datetime.datetime.today().strftime("%Y-%m-%d")
                filelist=self.logger.getLogFiles(starttime,endtime)
                for file in filelist:
                    self.upload_object(buckname, f"{file.split('/')[-1].split('.')[0]}_{station_id}.txt", file)
            #如果不存在,则直接上传out文件
            else:
                self.upload_object(buckname,  f"{station_id}.txt", curPath)
        except Exception as ex:
            # 删除当前文件
            self.logger.get_log().info(f"文件上传异常，{ex}")
            print(ex)

    # 启动一个线程任务
    def start_uploadlog(self):
        # threading.Thread(target=upload_img,args=(buckname,file_object,m0,m1)).start()
        threading.Thread(target=self.upload_log, args=()).start()


if __name__ == '__main__':
    buck_name = "uav-test"
    #ut=MiniUtils()
    #ut.start_uploadfile(buck_name,'err-gyy-jk.log')
    #start_uploadfile(buck_name,"error-jk.log")

