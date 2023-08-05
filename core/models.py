from django.db import models
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin

class Account(models.Model):
    username=models.CharField(max_length=255,unique=True)
    auth_id=models.CharField(max_length=255,)

    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)
    
    USERNAME_FIELD='username'
    REQUIRED_FIELDS =[]

    objects=UserManager
    

class PhoneNumber(models.Model):
    number = models.CharField(max_length=16)
    account = models.ForeignKey(Account, related_name='phone_numbers', on_delete=models.CASCADE)

    def __str__(self):
        return self.number
    
    
