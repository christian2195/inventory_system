# src/apps/returns/models.py
from django.db import models
from apps.inventory.models import Product, Client
from apps.dispatch_notes.models import DispatchNote

class ReturnNote(models.Model):
    return_number = models.CharField(max_length=50, unique=True)
    return_date = models.DateTimeField(auto_now_add=True)
    dispatch_note = models.ForeignKey(DispatchNote, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    returned_by = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='PENDING')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Devolución #{self.return_number}"

class ReturnItem(models.Model):
    return_note = models.ForeignKey(ReturnNote, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.description} - {self.quantity} unidades"