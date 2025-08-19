from django.contrib import admin
from .models import Product, Supplier, Warehouse

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'current_stock', 'min_stock', 'supplier', 'warehouse')
    list_filter = ('supplier', 'warehouse')
    search_fields = ('code', 'description', 'supplier__name')
    list_editable = ('current_stock',)
    
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'phone')
    search_fields = ('name',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)