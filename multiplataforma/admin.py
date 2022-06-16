from django.contrib import admin

from .models import PercentCommission, ImagesCarrousel


admin.site.site_header = "ADMINISTRADOR MYMULTIPLATAFORMA"
admin.site.site_title = "ADMINISTRADOR MYMULTIPLATAFORMA"
admin.site.index_title = "Bienvenidos al portal de ADMINISTRADOR de MYMULTIPLATAFORMA"

@admin.register(PercentCommission)
class PercentCommissionAdmin(admin.ModelAdmin):
   list_display = ( 'percent','date')
   fields  = ['percent' ]


@admin.register(ImagesCarrousel)
class ImagesCarrouselAdmin(admin.ModelAdmin):
   list_display = ( 'image','date')
   fields  = ['image' ]