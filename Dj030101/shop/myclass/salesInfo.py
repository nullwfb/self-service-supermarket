import pymysql
from Dj030101.settings import *
from django.http import HttpResponse

class SalesDetail:
    def __init__(self):
        self.serialnum = ""  # 流水单号
        self.totalnum = 0   # 商品总数
        self.totalmoney = 0.0  # 商品总金额
        self.username = "" # 用户名
        self.buytime = "" # 购买时间
        self.detail_list = []  # 购买的明细

    def get_serial_info(self):
        """
        获取当前流水单号的信息 
        :return: 
        """
        # =========去数据库读取模块信息======
        # 实例化mysqL连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 创建指针
        cursor = mysql_db.cursor()
        # 准备SQL语句

        sql = "Select SerialNumber, TotalNumber,TotalPrice,UserName,BuyTime " \
              "from SalesList As T1 Left Outer Join Login As T2 on T1.LoginId = T2.LoginId " \
              "where SerialNumber = '%s'" % (self.serialnum)
        try:
            cursor.execute(sql)
            serial_info  = cursor.fetchone()  # ((),(),(),())
            # 通过结果赋值
            self.totalnum = serial_info[1]
            self.totalmoney = serial_info[2]
            self.username = serial_info[3]
            self.buytime = serial_info[4]

        except Exception as e:
            return HttpResponse("读取数据库数据出现异常，具体原因：" + str(e))
        finally:
            mysql_db.close()

    def get_detail_info(self):
        # 实例化mysqL连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 创建指针
        cursor = mysql_db.cursor()
        # 准备SQL语句

        sql = "Select SerialNumber,ProductId,ProductName,Unit,UnitPrice,Number,Money " \
              "from SalesListDetail where SerialNumber= '%s'" %(self.serialnum)

        try:
            cursor.execute(sql)
            self.detail_list = cursor.fetchall()  # ((),(),(),())
            # 通过结果赋值

        except Exception as e:
            return HttpResponse("读取数据库数据出现异常，具体原因：" + str(e))
        finally:
            mysql_db.close()

