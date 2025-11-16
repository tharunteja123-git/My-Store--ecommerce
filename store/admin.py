'''from django.contrib import admin
from .models import Product, Category

# Register your models here.
admin.site.register(Product)
admin.site.register(Product)
admin.site.register(Category)'''

from django.contrib import admin
from .models import Product, Category

# Customize how Product appears in the admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')   # columns shown in list view
    list_filter = ('category', 'stock')                     # filters on the right side
    search_fields = ('name', 'description')                 # search bar fields

# Register models with admin site
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)

