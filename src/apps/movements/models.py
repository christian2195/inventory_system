# src/apps/movements/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Client
from django.contrib.auth.models import User
from django.db.models import F

class Movement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name="Tipo de Movimiento")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    date = models.DateTimeField(default=timezone.now, verbose_name="Fecha")
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    delivered_to = models.CharField(max_length=255, null=True, blank=True, verbose_name="Entregado a")

    def __str__(self):
        return f'{self.product.description} - {self.get_movement_type_display()}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Actualizar stock del producto
        if is_new:
            product = self.product
            if self.movement_type == 'IN':
                product.current_stock = F('current_stock') + self.quantity
            elif self.movement_type == 'OUT':
                product.current_stock = F('current_stock') - self.quantity
            product.save()

class Entry(models.Model):
    # This model might not be necessary if 'Movement' handles all types.
    # It's included here to match the view, but you might want to simplify later.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    # ... other fields