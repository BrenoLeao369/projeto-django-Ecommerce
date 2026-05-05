from django.contrib import admin
from . import models
# Register your models here.

class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    extra = 1

class ProdutoAdmin(admin.ModelAdmin):
    inlines = [
        VariacaoInline
    ]

admin.site.register(models.Product)
admin.site.register(models.Variacao)