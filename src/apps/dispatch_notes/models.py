# src/apps/dispatch_notes/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Client
from django.contrib.auth.models import User

class DispatchNote(models.Model):
    DISPATCH_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('DISPATCHED', 'Despachada'),
        ('CANCELLED', 'Cancelada'),
    ]

    dispatch_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    dispatch_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=DISPATCH_STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    
    def __str__(self):
        return f'Nota de Despacho #{self.dispatch_number}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total = sum(item.subtotal for item in self.items.all())
        super().save(update_fields=['total'])


class DispatchItem(models.Model):
    dispatch_note = models.ForeignKey(DispatchNote, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.description} - {self.quantity}'