from django.contrib import admin

# Register your models here.
from auth_system.models import MyUser

admin.site.register(MyUser)