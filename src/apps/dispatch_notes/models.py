# src/apps/dispatch_notes/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Client, Supplier
from django.contrib.auth.models import User

class DispatchNote(models.Model):
    DISPATCH_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('DISPATCHED', 'Despachada'),
        ('CANCELLED', 'Cancelada'),
    ]

    dispatch_number = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Número de Nota")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    dispatch_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Despacho")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    status = models.CharField(max_length=20, choices=DISPATCH_STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Total")

    # Nuevos campos del PDF
    beneficiary = models.CharField(max_length=100, null=True, blank=True, verbose_name="Beneficiario")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    order_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Número de Pedido")
    driver_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre del Conductor")
    driver_id = models.CharField(max_length=20, null=True, blank=True, verbose_name="Cédula del Conductor")
    vehicle_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tipo de Vehículo")
    vehicle_color = models.CharField(max_length=30, null=True, blank=True, verbose_name="Color del Vehículo")
    license_plate = models.CharField(max_length=15, null=True, blank=True, verbose_name="Placa")

    class Meta:
        verbose_name = "Nota de Despacho"
        verbose_name_plural = "Notas de Despacho"

    def __str__(self):
        return f'Nota de Despacho #{self.dispatch_number}'

    def save(self, *args, **kwargs):
        self.total = sum(item.subtotal for item in self.items.all())
        super().save(*args, **kwargs)

class DispatchItem(models.Model):
    dispatch_note = models.ForeignKey(DispatchNote, related_name='items', on_delete=models.CASCADE, verbose_name="Nota de Despacho")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Subtotal")
    
    # Nuevos campos del PDF
    brand = models.CharField(max_length=50, null=True, blank=True, verbose_name="Marca")
    model = models.CharField(max_length=50, null=True, blank=True, verbose_name="Modelo")

    class Meta:
        verbose_name = "Artículo de Despacho"
        verbose_name_plural = "Artículos de Despacho"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.description} - {self.quantity}'