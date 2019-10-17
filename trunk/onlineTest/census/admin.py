from django.contrib import admin
from census.models import Census, Weights
# Register your models here.

class CensusAdmin(admin.ModelAdmin):
    list_display = ['id', 'registered_users', 'choices', 'programms', 'fills', 'save_time']

class WeightsAdmin(admin.ModelAdmin):
    list_display = ['id', 'pythons', 'javas', 'cpps', 'begins', 'advances', 'savetime']
admin.site.register(Weights, WeightsAdmin)
admin.site.register(Census, CensusAdmin)
