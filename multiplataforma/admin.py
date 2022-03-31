from django.contrib import admin

from .models import PercentCommission


admin.site.site_header = "ADMINISTRADOR MYMULTIPLATAFORMA"
admin.site.site_title = "ADMINISTRADOR MYMULTIPLATAFORMA"
admin.site.index_title = "Bienvenidos al portal de ADMINISTRADOR de MYMULTIPLATAFORMA"

@admin.register(PercentCommission)
class PercentCommissionAdmin(admin.ModelAdmin):
   list_display = ( 'percent','date')
   fields  = ['percent' ]
