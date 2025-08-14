# inventory/admin.py

from django.contrib import admin
from .models import Product, Movement, Supplier, UnitOfMeasurement, MovementType

# Clase de administración para el modelo Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'description',
        'unit_of_measurement',
        'current_stock',
        'min_stock',
        'unit_price'
    )
    list_filter = ('unit_of_measurement',)
    search_fields = ('code', 'description',)
    list_editable = ('current_stock', 'min_stock', 'unit_price',)

# Clase de administración para el modelo Movement
@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = (
        'movement_number',
        'date',
        'product',
        'movement_type',
        'quantity',
        'total_price'
    )
    list_filter = ('movement_type', 'date', 'product')
    search_fields = ('movement_number', 'product__description', 'product__code',)
    autocomplete_fields = ['product', 'supplier']
    date_hierarchy = 'date'
    readonly_fields = ('movement_number', 'total_price', 'created_at', 'updated_at')

# Registro simple para los modelos restantes
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'contact', 'phone',)
    search_fields = ('name', 'code',)

@admin.register(UnitOfMeasurement)
class UnitOfMeasurementAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation',)
    search_fields = ('name', 'abbreviation',)

@admin.register(MovementType)
class MovementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_entry',)
    search_fields = ('name', 'code',)