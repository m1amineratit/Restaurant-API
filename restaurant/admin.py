from django.contrib import admin
from .models import Category, Menu, Cart, Order, OrderItem 

# Register your models here.


admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)