from django.db import models
from api.managers import MyUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class Rol(models.Model):
    user_type = models.CharField(max_length=30)

    def __str__(self):
        return str(self.user_type)

class MyUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=150,unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)

    def to_json(self):
        return {
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'rol_user_type': self.rol.user_type,
            'is_active': self.is_active,
            'is_staff': self.is_staff,            
        }

class ProductCategory (models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)

class Suplier (models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=150,unique=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    direction = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.name)

class Product (models.Model):
    presentation = models.CharField(max_length=30)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    detail = models.CharField(max_length=70)
    brand = models.CharField(max_length=30)
    codigo = models.CharField(max_length=30)
    duedate = models.DateField(blank=True, null=True)
    url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return str(self.detail) + ' (' + self.brand + ')'

    def to_json(self):
        return {
            'presentation': self.presentation,
            'category': self.category.name,
            'detail': self.detail,
            'brand': self.brand,
            'codigo': self.codigo,
            'duedate': self.duedate,
            'url': self.url
        }

class ProductHistory (models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    suplier = models.ForeignKey(Suplier, on_delete=models.CASCADE)
    unit_cost_price = models.FloatField()
    unit_sales_price = models.FloatField()
    units_purchased = models.IntegerField(default=0)

    def __str__(self):
        return str(self.product) + ' - ' + str(self.suplier) + ' - ' + str(self.date)

class Inventory (models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sales_price = models.FloatField()

    def __str__(self):
        return str(self.product) + ' - ' + str(self.quantity) + ' - ' + str(self.sales_price)

class Sale (models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return str(self.product) + ' - ' + str(self.quantity) + ' - ' + str(self.date)


class CarouselImage (models.Model):
    url = models.TextField(max_length=200)

    def __str__(self):
        return str(self.url)
