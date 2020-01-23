from datetime import datetime
import random
import pymysql
from Dj030101.settings import *
from django.http import HttpResponse

class Customer:
    # 构造函数
    def __init__(self):
        self.serialnum = ""  # 存储生成的流水单号
        self.buy_list = []   # 存储了当前扫描的商品
        self.total_number = 0 # 存储商品总量
        self.total_money = 0.0  # 存储总金额
        self.receive_money = 0.0 #存储收款金额
        self.return_money = 0.0  # 存储找零金额
    def get_serialnum(self):
        """
        生成流水单号
        :return: 
        """
        # 获取当前的系统事件
        dt = datetime.now()
        # 生成流水单号
        self.serialnum = '%04d%02d%02d%02d%02d%02d' % (dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
        # 生成4位的随机数
        temp = random.randint(0, 9999)
        # 附加到流水单号的尾部
        self.serialnum += '%04d' % (temp)

    def get_procduct_by_barcode(self, barcode):
        """
        通过条形码到数据库中找到商品
        :param barcode: 
        :return: 
        """
        # 实例化数据库连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 定义一个指针
        cursor = mysql_db.cursor()
        # 准备SQL语句
        sql = " Select ProductId,BarCode,ProductName,Unit,UnitPrice from Product " \
              " where BarCode = '%s' " % (barcode)

        try:
            # 执行SQL获取结果
            cursor.execute(sql)
            # 获取结果
            product = cursor.fetchone()  # 元组类型
            #添加
            self.add_product_to_buylist(product)

        except Exception as e:
            self.error_info = "联系数据库出现异常，具体原因：" + str(e)
        finally:
            mysql_db.close()

    def add_product_to_buylist(self, product):
        """
        添加商品到buylist 
        :return: 
        """
        # 准备数据
        temp_dict = {
            "ProductId": product[0],
            "ProductName": product[2],
            "Unit": product[3],
            "UnitPrice": product[4],
            "Number":1,
            "Money": product[4]
        }
        # 添加到list
        if len(self.buy_list) == 0:
            self.buy_list.append(temp_dict)
        else:
            # 遍历当前的buy_list
            for index in range(len(self.buy_list)):
                # 判断是否存在
                if temp_dict['ProductId'] == self.buy_list[index]['ProductId']:
                    self.buy_list[index]["Number"] += 1
                    self.buy_list[index]["Money"] = self.buy_list[index]["UnitPrice"] * self.buy_list[index]["Number"]
                    break
                if index == len(self.buy_list)-1:
                    self.buy_list.append(temp_dict)

    def delete_product_from_buylist(self,productId):
        """
        删除列表中的商品
        :param productId: 
        :return: 
        """
        # 遍历buyList
        for index in range(len(self.buy_list)):
            # 判断是否相等
            if self.buy_list[index]["ProductId"] == productId:
                self.buy_list.pop(index)
                break

    def get_total_info(self):
        """
        获取购买商品总数量和总金额
        :return: 
        """
        self.total_number = 0
        self.total_money = 0.0
        # 遍历
        for product in self.buy_list:
            self.total_number += product["Number"]
            self.total_money += product["Money"]

        # 保留金额的两位小数
        self.total_money = round(self.total_money,2)

    def get_receive_return_money(self, receive):
        """
        赋值收款和找零金额
        :param receive: 
        :return: 
        """
        self.receive_money = round(float(receive), 2)
        self.return_money = round(self.receive_money - self.total_money,2)

    def submit(self, loginId):
        """
        提交到数据库
        :return: 
        """
        # 实例化数据库连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 定义一个指针
        cursor = mysql_db.cursor()
        # 准备SQL语句 --- 插入SalesList，插入到SalesListDetail ,更新Product ,通过List
        sql_list = []
        # 插入到SalesList --- 一条
        sql = "Insert Into SalesList (SerialNumber,TotalNumber,TotalPrice,ReceiveMoney,ReturnMoney,LoginId,BuyTime) " \
              "Values('%s',%d,%.2f,%.2f,%.2f,'%s','%s')" %(self.serialnum,self.total_number,self.total_money,
                                                          self.receive_money,self.return_money,loginId,datetime.now())
        sql_list.append(sql)

        # 插入到SalesListDetail  ---- 有多少商品就多少条
        # 更新库存 --- 修改Produce === 有多少商品就多少条
        for product in self.buy_list:
            # 插入到SalesListDetail
            sql01 = "Insert Into SalesListDetail(SerialNumber, ProductId, ProductName, Unit, UnitPrice, Number, Money) " \
                    "Values('%s','%s','%s','%s',%.2f,%d,%.2f)" %(self.serialnum, product['ProductId'],product['ProductName'],
                                                                 product['Unit'],product['UnitPrice'],product['Number'],product['Money'])
            sql_list.append(sql01)
            # 修改Produce
            sql02 = "Update Product Set Inventory=Inventory-%d  where ProductId='%s'" % (product['Number'],product['ProductId'])
            sql_list.append(sql02)

        try:
            # 遍历sql_list
            for sql in sql_list:
                # 执行SQL获取结果
                cursor.execute(sql)
            # 使用提交更改
            mysql_db.commit()

        except Exception as e:
            # rollback -- 回滚
            mysql_db.rollback()
            # 报错
            return HttpResponse("提交出现异常，具体原因：" + str(e))
        finally:
            mysql_db.close()






if __name__ == '__main__':
    obj = Customer()
    obj.get_procduct_by_barcode("6907992500133" )
    print(print(obj.buy_list))