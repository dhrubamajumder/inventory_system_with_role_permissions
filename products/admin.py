from django.contrib import admin
from .models import Category, Product, Supplier, Purchase, Stock, Role, Permission

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Purchase)
admin.site.register(Stock)
admin.site.register(Role)
admin.site.register(Permission)