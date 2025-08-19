# src/apps/inventory/models.py
from django.db import models
from apps.inventory.models import Product

class Quotation(models.Model):
    client = models.CharField(max_length=100)
    quotation_number = models.CharField(max_length=50, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)