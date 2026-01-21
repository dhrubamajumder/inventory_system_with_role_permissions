

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
    # path('purchase/<int:pk>/delete', views.purchase_detete, name='purchase_delete'),
    
    path('supplier/create/', views.supplier_create, name='supplier_create'),
    path('supplier/list/', views.supplier_list, name='supplier_list'),
    path('supplier/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('supplier/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
]
