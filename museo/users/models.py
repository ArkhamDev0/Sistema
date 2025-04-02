from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=True)  # Solo admins acceden al panel Django
    
    # Campos adicionales si necesitas
    telefono = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.username

    # Sobreescribir permisos
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin