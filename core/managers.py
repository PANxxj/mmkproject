from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

class UserManager(BaseUserManager):
    def create_user(self,username,auth_id,**kwargs):
        if not username:
            raise ValueError(_('Please enter an email address'))
        user=self.model(username=username,**kwargs)
        user.set_password(auth_id)
        user.save()
        return user
    def create_superuser(self,username,auth_id,**kwargs):
        kwargs.setdefault('is_staff',True)
        kwargs.setdefault('is_superuser',True)
        kwargs.setdefault('is_active',True)
        
        if kwargs.get('is_staff') is not True:
            raise ValueError(_('superuser must have is_staff=True'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(_('superuser must have is_superuser=True'))
        return self.create_user(username,auth_id,**kwargs)
