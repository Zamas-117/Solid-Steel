from django.contrib import admin
from django import forms
from product.models import UserAccount, Supplier, Client, ClientAddress, Product, Order, OrderItem, Shipment, Payment, ShoppingCart, WishItem, PasswordReset, SupplierSales, Recycle, SupplierPaymentMethodModel
# Register your models here.

admin.site.register(UserAccount)
admin.site.register(Supplier)
admin.site.register(Client)
admin.site.register(ClientAddress)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Shipment)
admin.site.register(Payment)
admin.site.register(ShoppingCart)
admin.site.register(WishItem)
admin.site.register(PasswordReset)
admin.site.register(SupplierSales)
admin.site.register(Recycle)
admin.site.register(SupplierPaymentMethodModel)

