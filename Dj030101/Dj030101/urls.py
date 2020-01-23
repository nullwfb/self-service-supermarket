""" Dj030101 URL Configuration

The 'urlpatterns' list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop import views as shop_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', shop_views.index, name='index'),
    path('login/', shop_views.login, name='login'),
    path('cashier/', shop_views.cashier, name='cashier'),
    path('cashier/add_product/', shop_views.add_product, name="add_product"),
    path('cashier/delete_product/', shop_views.delete_product, name="delete_product"),
    path('cashier/get_return/', shop_views.get_return_money, name="get_return"),
    path('cashier/cancel/', shop_views.cashier_cancel, name="cashier_cancel"),
    path('cashier/submit/', shop_views.cashier_submit, name="cashier_submit"),
    path('main/', shop_views.main, name='main'),
    path('main/sales_query/', shop_views.sales_query, name='sales_query'),
    path('main/salesdetail_query/', shop_views.salesdetail_query, name='salesdetail_query'),
]
