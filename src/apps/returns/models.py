# src/apps/returns/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Client
from apps.dispatch_notes.models import DispatchNote, DispatchItem
from django.contrib.auth.models import User

class ReturnNote(models.Model):
    RETURN_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSED', 'Procesada'),
        ('CANCELLED', 'Cancelada'),
    ]

    return_number = models.CharField(max_length=50, unique=True)
    dispatch_note = models.ForeignKey(DispatchNote, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    return_date = models.DateTimeField(default=timezone.now)
    returned_by = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f'Nota de Devolución #{self.return_number}'

class ReturnItem(models.Model):
    return_note = models.ForeignKey(ReturnNote, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.description} - {self.quantity}'