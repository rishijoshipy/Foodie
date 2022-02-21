from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password,is_staff,is_superuser,is_enduser,is_owner,is_auth, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_enduser=is_enduser,
            is_owner=is_owner,
            is_auth=is_auth,
            is_verify=False,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None,**extra_fields):
        return self._create_user(email, password,False,False,**extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password,True,True,True,True,True,**extra_fields)
    