from Dj030101.settings import *
from datetime import datetime
import pymysql

class UserSignin:
    # 构造函数
    def __init__(self):
        self.logins = []  # 读取数据库中所有的账号
        self.loginId = ""  # 用户输入的登录账号
        self.loginPwd = ""  # 用户输入的登录密码
        self.error_info = ""  # 记录错误信息
        self.signin_result = False  # 记录验证的结果
        self.position_name = ""  # 记录当前登录的用户的职位
        self.password_error_times = 0  # 密码错误次数
        self.current_username = ""  # 记录了当前的登录姓名

    def load_logins(self):
        """
        读取数据库中所有的用户名和密码，存储在Logins集合 
        :return: 
        """
        # 实例化数据库连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 定义一个指针
        cursor = mysql_db.cursor()
        # 准备SQL语句
        sql = " Select LoginId,LoginPwd,UserName,IsEnable,PositionName " \
              " from Login As T1 INNER JOIN Position As T2 on T1.PositionId = T2.PositionId "

        try:
            # 执行SQL获取结果
            cursor.execute(sql)
            self.logins = cursor.fetchall()

        except Exception as e:
            self.error_info = "联系数据库出现异常，具体原因：" + str(e)
        finally:
            mysql_db.close()

    def signin(self):
        """
        进行身份验证
        :return: 
        """
        # 从数据库中读取数据
        self.load_logins()
        # 遍历集合
        for index in range(len(self.logins)):
            # 如何登录名匹配
            if self.logins[index][0] == self.loginId:
                # 判断是否禁用
                if self.logins[index][3] == 0:
                    self.error_info = "账号已禁用！请联系管理员"
                    self.signin_result = False
                    break
                # 如果密码匹配：
                if self.logins[index][1] == self.loginPwd:
                    # 身份验证成功
                    self.signin_result = True
                    # 记录当前的职位
                    self.position_name = self.logins[index][4]
                    # 记录当前的登录姓名
                    self.current_username = self.logins[index][2]
                    # 更新上次登录时间
                    self.update_last_login_time()
                    # 成功后把错误的次数清零
                    self.password_error_times = 0
                    # 跳出
                    break
                else:
                    # 次数+1
                    self.password_error_times += 1
                    # 判断是否到三次
                    if self.password_error_times == 3:
                        # 禁用账号
                        self.diable_login()
                        # 错误信息
                        self.error_info = "密码错误三次，账号已禁用！"
                        self.signin_result = False
                    else:
                        self.error_info = "密码错误！"
                        self.signin_result = False
                    break

            # 判断用户名是否存在
            if index == len(self.logins) - 1:
                self.error_info = "登录账号不存在！"
                self.signin_result = False

    def diable_login(self):
        # 实例化数据库连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 定义一个指针
        cursor = mysql_db.cursor()
        # 准备SQL语句
        sql = " Update Login Set IsEnable = 0 Where LoginId = '%s'" % self.loginId

        try:
            # 执行SQL获取结果
            cursor.execute(sql)
            # 提交
            mysql_db.commit()

        except Exception as e:
            # 撤销
            mysql_db.rollback()
            self.error_info = "联系数据库出现异常，具体原因：" + str(e)
        finally:
            mysql_db.close()

    def update_last_login_time(self):
        """
        写入上次登录的事件
        :return: 
        """
        # 记录当前系统事件
        dt01 = datetime.now()
        # 实例化数据库连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 定义一个指针
        cursor = mysql_db.cursor()
        # 准备SQL语句
        sql = " Update Login Set LastLoginTime = '%s' Where LoginId = '%s'" % (dt01, self.loginId)

        try:
            # 执行SQL获取结果
            cursor.execute(sql)
            # 提交
            mysql_db.commit()

        except Exception as e:
            # 撤销
            mysql_db.rollback()
            self.error_info = "联系数据库出现异常，具体原因：" + str(e)
        finally:
            mysql_db.close()


if __name__ == '__main__':
    obj = UserSignin()
    obj.loginId ='2001'
    obj.loginPwd ='123.com'
    obj.signin()
    print(obj.logins)
    print(obj.signin_result)

