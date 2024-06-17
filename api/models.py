from django.db import models
from api.managers import MyUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class Rol(models.Model):
    user_type = models.CharField(max_length=30)

    def __str__(self):
        return self.user_type
    
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
        return self.email
    
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