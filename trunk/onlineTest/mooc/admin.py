from django.contrib import admin
from mooc.models import Resource,Week,Type
# Register your models here.
admin.site.register(Resource)
admin.site.register(Type)
admin.site.register(Week)