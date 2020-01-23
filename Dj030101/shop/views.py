from django.shortcuts import render, redirect, reverse
import pymysql
from django.http import HttpResponse
from Dj030101.settings import *
from .myclass import signin
from .myclass import shop_cashier
from .myclass import salesInfo
from datetime import datetime


# Create your views here.
# =========实例化身份验证的对象=======
login_obj = signin.UserSignin()
# =========实例化收银模块的对象=======
current_customer = shop_cashier.Customer()
# =========实例化销售明细的对象=======
current_serial = salesInfo.SalesDetail()




def index(request):
    return redirect(reverse('login'))

# ===== 用户登录 传统写法 =====
"""
def login(request):
    # 实现登录页面

    if request.method == 'GET':
        # 如果是GET方式，打开登录界面
        return render(request, 'login.html')

    elif request.method == "POST":
        # 定义一个变量存储登录过程中错误信息
        error_info = ""
        logins = []

        # 验证输入的用户名和密码
        # 1. 获取输入的用户名和密码
        login_id = request.POST.get('login')
        login_pwd = request.POST.get('password')

        # 2. 获取数据库中数据
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cursor = mysql_db.cursor()
        sql = " Select LoginId,LoginPwd,UserName,IsEnable,PositionName " \
              " from Login As T1 INNER JOIN Position As T2 on T1.PositionId = T2.PositionId "

        try:
            # 执行SQL获取结果
            cursor.execute(sql)
            logins = cursor.fetchall()

        except Exception as e:
            error_info = "联系数据库出现异常，具体原因：" + str(e)
        finally:
            mysql_db.close()

        # 3. 用输入的账号在数据库中判断
        for index in range(len(logins)):
            # 如何登录名匹配
            if logins[index][0] == login_id:
                # 判断是否禁用
                if logins[index][3] == 0:
                    error_info = "账号已禁用！请联系管理员"
                    break
                # 如果密码匹配：
                if logins[index][1] == login_pwd:
                    # 判断职位
                    return redirect(reverse('cashier'))
                else:
                    error_info = "密码错误！"
                    break

            # 判断用户名是否存在
            if index == len(logins) - 1:
                error_info = "登录账号不存在！"

        # 很多场景没有处理：比如：登录名不存在，密码错误，已经禁用，按职位做跳转！
        return render(request, 'login.html', context={'loginId': login_id,
                                                      'loginPwd': login_pwd,
                                                    'info': error_info})
"""

# ==== 用户登录 推荐写法 ====
def login(request):

    if request.method == 'GET':
        # 如果是GET方式，打开登录界面
        return render(request, 'login.html')

    elif request.method == "POST":
        # 获取登录的用户名和密码并赋值实例变量
        login_obj.loginId = request.POST.get('login')
        login_obj.loginPwd = request.POST.get('password')
        # 进行身份验证
        login_obj.signin()
        # 根据结果返回
        if login_obj.signin_result: # 如果是TRUE
            # 判断职位
            if "收银" in login_obj.position_name:
                return redirect(reverse('cashier') + "?username=" + login_obj.current_username)
            elif "管理员" in login_obj.position_name:
                return redirect(reverse('main') + "?username=" + login_obj.current_username)
        else:
            return render(request, 'login.html', context={'loginId': login_obj.loginId,
                                                          'loginPwd': login_obj.loginPwd,
                                                          'info': login_obj.error_info})

def cashier(request):
    """
    收银页面
    :param request: 
    :return: 
    """
    # 获取URL中的用户名
    username = request.GET.get("username")
    if username:
        if len(current_customer.serialnum) == 0:
            # 自动生成
            current_customer.get_serialnum()

        # 统计数量和金额
        current_customer.get_total_info()
        # 加载页面
        return render(request, 'cashier.html', context={'customer': current_customer,
                                                        'username': username})
    else:
        return redirect(reverse('login'))

def main(request):
    """
    管理员主页面
    :param request: 
    :return: 
    """
    username = request.GET.get("username")
    if username:
        # =========去数据库读取模块信息======
        # 实例化mysqL连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 创建指针
        cursor = mysql_db.cursor()
        # 准备SQL语句
        sql = " Select ModuleId, ModuleName,URL, ICON, Priority from AdminModules " \
              " Order By Priority DESC "

        try:
            cursor.execute(sql)
            modules = cursor.fetchall()  # ((),(),(),())
        except Exception as e:
            return HttpResponse("读取数据库数据出现异常，具体原因："+str(e))
        finally:
            mysql_db.close()

        # 拼接URL
        url_list = []
        for module in modules:
            temp = []
            temp.append(module[0])
            temp.append(module[1])
            temp.append(reverse(module[2]) + "?username=" + login_obj.current_username)
            temp.append(module[3])
            temp.append(module[4])
            # 附加到url_list
            url_list.append(temp)



        return render(request, 'main.html', context={'username': username,
                                                     'modules': url_list,

                                                     })
    else:
        return redirect(reverse('login'))

def sales_query(request):
    """
    交易概况页面
    :param request: 
    :return: 
    """

    if request.method == "GET":
        username = request.GET.get("username")
        # 判断是否登录
        if username is None:
            return redirect(reverse('login'))
        else:
            # =========去数据库读取模块信息======
            # 实例化mysqL连接
            mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
            # 创建指针
            cursor = mysql_db.cursor()
            # 准备SQL语句
            sql = "Select SerialNumber, TotalNumber,TotalPrice,ReceiveMoney,ReturnMoney,UserName,BuyTime " \
                  "from SalesList As T1 Left Outer Join Login As T2 on T1.LoginId = T2.LoginId " \
                  "Order By BuyTime DESC"
            try:
                cursor.execute(sql)
                sales_list = cursor.fetchall()  # ((),(),(),())
                return render(request, 'sales_query.html', context={'sales_list': sales_list, 'username': username})
            except Exception as e:
                return HttpResponse("读取数据库数据出现异常，具体原因：" + str(e))
            finally:
                mysql_db.close()
    elif request.method == "POST":
        # 获取现在时间
        dt = datetime.now()
        # 把所有的条件采集到字典中
        query_dict = {}
        query_dict['serialnum'] = request.POST.get("serialnum") # 单号：字符串 Like
        query_dict['username'] = request.POST.get("username") # 姓名：字符串 Like
        query_dict['start'] = request.POST.get("start")  # buytime,时间日期类型，无法用Like
        query_dict['end'] = request.POST.get("end")# buytime,时间日期类型，无法用Like
        if len(query_dict['start']) == 0:
            query_dict['start'] = '%d-01-01' %(dt.year)
        if len(query_dict['end']) == 0:
            query_dict['end'] = '%04d-%02d-%02d %02d:%02d:%02d' %(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

        # =========去数据库读取模块信息======
        # 实例化mysqL连接
        mysql_db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        # 创建指针
        cursor = mysql_db.cursor()
        # 准备SQL语句
        sql = "Select SerialNumber, TotalNumber,TotalPrice,ReceiveMoney,ReturnMoney,UserName,BuyTime " \
                  "from SalesList As T1 Left Outer Join Login As T2 on T1.LoginId = T2.LoginId " \
                  " where SerialNumber like '%s' and UserName like '%s' and BuyTime BETWEEN '%s' and '%s'" \
                  "Order By BuyTime DESC " %('%'+ query_dict['serialnum']+'%','%'+ query_dict['username']+'%',query_dict['start'],
                                                 query_dict['end'])
        print(sql)
        try:
            cursor.execute(sql)
            sales_list = cursor.fetchall()  # ((),(),(),())
            return render(request, 'sales_query.html', context={'sales_list': sales_list,
                                                                'username': login_obj.current_username,
                                                                'query':query_dict
                                                                }
                          )
        except Exception as e:
            return HttpResponse("读取数据库数据出现异常，具体原因：" + str(e))
        finally:
            mysql_db.close()


def salesdetail_query(request):

    # 获取传递的值
    username = request.GET.get('username')
    serialnum = request.GET.get('serialnum')
    # 判断是否登录
    if username is None:
        return redirect(reverse('login'))
    else:
        # 把流水号传递给对象
        current_serial.serialnum = serialnum
        # 获取概况信息
        current_serial.get_serial_info()
        # 获取该流水的明细信息
        current_serial.get_detail_info()

        # 传递给模板页面
        return render(request, 'salesdetail_query.html', context={'username':username,
                                                                  'serial':current_serial
                                                                  }
                      )

def add_product(request):
    """
    添加一个商品
    :param request: 
    :return: 
    """
    # 获取当前的条形码
    barcode = request.GET.get('barcode')
    # 添加到buy_list
    current_customer.get_procduct_by_barcode(barcode)
    # 跳转到收银页面
    return redirect(reverse('cashier') + "?username=" + login_obj.current_username)

def delete_product(request):
    """
    删除商品 
    :param request: 
    :return: 
    """
    # 获取点击的商品编号
    productId = request.GET.get("productId")

    #执行删除
    current_customer.delete_product_from_buylist(productId)

    # 跳转
    return redirect(reverse('cashier') + "?username=" + login_obj.current_username)

def get_return_money(request):
    """
    计算找零金额
    :param request: 
    :return: 
    """
    # 获取收款金额
    receive = request.GET.get("receive")
    print(receive)
    # 赋值
    current_customer.get_receive_return_money(receive)
    # 跳转
    return redirect(reverse('cashier') + "?username=" + login_obj.current_username)

def cashier_cancel(request):
    """
    取消当前订单
    :param request: 
    :return: 
    """
    current_customer.buy_list.clear() # 清空当前的列表
    current_customer.serialnum = ""  # 清空当前的单号
    current_customer.total_number = 0  # 存储商品总量
    current_customer.total_money = 0.0  # 存储总金额
    current_customer.receive_money = 0.0 #存储收款金额
    current_customer.return_money = 0.0  # 存储找零金额
    # 跳转
    return redirect(reverse('cashier') + "?username=" + login_obj.current_username)

def cashier_submit(request):
    """
    提交到数据库
    :param request: 
    :return: 
    """
    # 提交到数据库
    current_customer.submit(login_obj.loginId)
    # 重新初始化顾客
    current_customer.buy_list.clear()  # 清空当前的列表
    current_customer.serialnum = ""  # 清空当前的单号
    current_customer.total_number = 0  # 存储商品总量
    current_customer.total_money = 0.0  # 存储总金额
    current_customer.receive_money = 0.0  # 存储收款金额
    current_customer.return_money = 0.0  # 存储找零金额
    # 跳转
    return redirect(reverse('cashier') + "?username=" + login_obj.current_username)





