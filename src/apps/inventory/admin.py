# src/apps/inventory/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Product, Supplier, Warehouse
from decimal import Decimal
import uuid

class ProductResource(resources.ModelResource):
    # Define campos personalizados con validación
    product_code = fields.Field(attribute='product_code', column_name='product_code')
    description = fields.Field(attribute='description', column_name='description')
    unit = fields.Field(attribute='unit', column_name='unit', default='UNIDAD')
    unit_price = fields.Field(attribute='unit_price', column_name='unit_price')
    current_stock = fields.Field(attribute='current_stock', column_name='current_stock', default=0)
    min_stock = fields.Field(attribute='min_stock', column_name='min_stock', default=0)
    max_stock = fields.Field(attribute='max_stock', column_name='max_stock', default=0)
    location = fields.Field(attribute='location', column_name='location', default='')
    category = fields.Field(attribute='category', column_name='category', default='')
    supplier_name = fields.Field(attribute='supplier__name', column_name='supplier', readonly=True)
    warehouse_name = fields.Field(attribute='warehouse__name', column_name='warehouse', readonly=True)
    
    class Meta:
        model = Product
        fields = ('product_code', 'description', 'unit', 'unit_price', 'current_stock', 
                 'min_stock', 'max_stock', 'location', 'category', 'supplier_name', 'warehouse_name')
        import_id_fields = ['product_code']
        exclude = ('id',)
    
    def before_import_row(self, row, **kwargs):
        """Preprocesar datos antes de importar"""
        # 1. Manejar product_code nulo o vacío - GENERAR UN CÓDIGO TEMPORAL
        if not row.get('product_code') or row.get('product_code') in ['None', 'null', '']:
            # Generar un código temporal único basado en UUID
            temp_code = f'TEMP_{uuid.uuid4().hex[:8].upper()}'
            row['product_code'] = temp_code
        
        # 2. Proporcionar valores por defecto para campos obligatorios
        if not row.get('unit_price') or row.get('unit_price') in ['None', 'null', '']:
            row['unit_price'] = '0.00'
        
        # 3. Asegurar que todos los campos numéricos tengan valores
        numeric_fields = ['current_stock', 'min_stock', 'max_stock']
        for field in numeric_fields:
            if not row.get(field) or row.get(field) in ['None', 'null', '']:
                row[field] = '0'
        
        # 4. Campos de texto
        if not row.get('unit') or row.get('unit') in ['None', 'null', '']:
            row['unit'] = 'UNIDAD'
        
        if not row.get('location'):
            row['location'] = ''
        
        if not row.get('category'):
            row['category'] = ''

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('product_code', 'description', 'unit_price', 'current_stock', 'min_stock', 'supplier', 'warehouse')
    list_filter = ('supplier', 'warehouse', 'category')
    search_fields = ('product_code', 'description', 'supplier__name')
    list_editable = ('current_stock', 'unit_price')
    
    # ELIMINA ESTE MÉTODO o corrígelo como se muestra en la Opción 2
    # def get_import_resource_kwargs(self, request, *args, **kwargs):
    #     """Pasar el request al resource para logging"""
    #     return {'request': request}

# Los otros admin permanecen igual
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'phone', 'email')
    search_fields = ('name', 'contact')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_main')
    search_fields = ('name', 'location')
    list_filter = ('is_main',)