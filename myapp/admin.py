from django.contrib import admin
from myapp import models

# Register your models here.

admin.site.register(models.ProductModel)
admin.site.register(models.CategoryModel)
admin.site.register(models.WishListModel)
admin.site.register(models.CartListModel)
admin.site.register(models.OrderListModel)
admin.site.register(models.MessageModel)