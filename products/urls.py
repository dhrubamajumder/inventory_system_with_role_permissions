

from unicodedata import name
from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_product, name='product_create'),
    path('list/', views.product_list, name='product_list'),
    path('<int:pk>/edit/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    path('category/create/', views.create_category, name='category_create'),
    path('categroy/list/', views.category_list, name='category_list'),
    path('category/<int:pk>/edit/', views.update_category, name='update_category'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    path('purchase/create/', views.create_purchase, name='purchase_create'),
    path('purchase/list/', views.purchase_list, name='purchase_list'),
    path('purchase/detail/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchase/<int:pk>/update/', views.purchase_update, name='purchase_update'),
    path('purchase/<int:pk>/delete', views.purchase_delete, name='purchase_delete'),
    
    path('supplier/create/', views.supplier_create, name='supplier_create'),
    path('supplier/list/', views.supplier_list, name='supplier_list'),
    path('supplier/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('supplier/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    path('permission/list/', views.permission_list, name='permission_list'),
    path('permission/create/', views.permission_create, name='permission_create'),
    
    path('role/list/', views.role_list, name='role_list'),
    path('role/create/', views.role_create, name='role_create'),
    path('role/<int:pk>/update/', views.role_update, name='role_update'),
    path('role/<int:pk>/delete/', views.role_delete, name='role_delete'),

    path('user/list/', views.user_list, name='user_list'),
    path('user/create/',  views.add_user, name='user_create'),
    path('users/edit/<int:id>/',  views.edit_user, name='edit_user'),
    path('users/delete/<int:id>/',  views.delete_user, name='delete_user'),
    
    path('system/list/', views.system_list, name='system_list'),
    path('system/', views.company_create, name='system'),
    path('system/<int:pk>/update/', views.system_update, name='system_update'),  
    
    path('stock/list/', views.low_stock_list, name='stock_list'),
    
    path('showsales/', views.collect_order_list, name='collect_order_list'),
    path('showsales/category/<int:category_id>/', views.collect_order_list, name='collect_order_list_by_category'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/category/<int:category_id>/', views.order_list, name='order_list_by_category'),
    
    path('product/orders/ajax/products/<str:category_id>/', views.ajax_products_by_category, name='ajax_products'),
    
    path('orders/save/', views.save_order, name='save_order'),
    
    path('orders/create/', views.create_order, name='create_order'),
    path('order/pending/', views.pending_order_list, name='pending_orders'),
    path('order/accept/<int:order_id>/', views.accept_order, name='accept_order'),

    path('sales/report/', views.sales_report_list, name='sales_report'),
    
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),


]
