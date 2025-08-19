# src/apps/inventory/models.py
from django.db import models

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    udm = models.CharField(max_length=20)  # Unidad de Medida
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.SET_NULL, null=True)
    min_stock = models.PositiveIntegerField(default=0)
    current_stock = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        app_label = 'inventory' 

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

class Warehouse(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)