# src/apps/reception_notes/models.py
from django.db import models
from apps.inventory.models import Supplier, Product

class ReceptionNote(models.Model):
    reception_number = models.CharField(max_length=50, unique=True)
    reception_date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    received_by = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='PENDING')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Recepción #{self.reception_number}"

class ReceptionItem(models.Model):
    reception_note = models.ForeignKey(ReceptionNote, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.description} - {self.quantity} unidades"