from django.contrib import admin
from . import models

# Register your models here.\

admin.site.register(models.Rol)
admin.site.register(models.MyUser)
admin.site.register(models.ProductCategory)
admin.site.register(models.Suplier)
admin.site.register(models.Product)
admin.site.register(models.ProductHistory)
admin.site.register(models.Inventory)
admin.site.register(models.Sale)
