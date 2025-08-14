from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    code = models.CharField(max_length=20, verbose_name="Código", blank=True, null=True)
    contact = models.CharField(max_length=100, verbose_name="Contacto", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    address = models.TextField(verbose_name="Dirección", blank=True, null=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
    
    def __str__(self):
        return self.name

class UnitOfMeasurement(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    abbreviation = models.CharField(max_length=10, verbose_name="Abreviatura")
    
    class Meta:
        verbose_name = "Unidad de Medida"
        verbose_name_plural = "Unidades de Medida"
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class Product(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    description = models.TextField(verbose_name="Descripción")
    unit_of_measurement = models.ForeignKey(
        UnitOfMeasurement, 
        on_delete=models.PROTECT, 
        verbose_name="Unidad de Medida"
    )
    current_stock = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)], 
        verbose_name="Stock Actual"
    )
    min_stock = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)], 
        verbose_name="Stock Mínimo"
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Precio Unitario"
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="Precio Total"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['description']
    
    def __str__(self):
        return f"{self.code} - {self.description}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.current_stock * self.unit_price
        super().save(*args, **kwargs)

class MovementType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    code = models.CharField(max_length=10, verbose_name="Código")
    is_entry = models.BooleanField(default=True, verbose_name="Es Entrada?")
    
    class Meta:
        verbose_name = "Tipo de Movimiento"
        verbose_name_plural = "Tipos de Movimiento"
    
    def __str__(self):
        return self.name

class Movement(models.Model):
    movement_number = models.CharField(max_length=20, unique=True, verbose_name="Número de Movimiento")
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT, 
        verbose_name="Producto"
    )
    movement_type = models.ForeignKey(
        MovementType, 
        on_delete=models.PROTECT, 
        verbose_name="Tipo de Movimiento"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], 
        verbose_name="Cantidad"
    )
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT, 
        verbose_name="Proveedor",
        blank=True, 
        null=True
    )
    delivered_to = models.CharField(
        max_length=200, 
        verbose_name="Entregado a", 
        blank=True, 
        null=True
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Precio Unitario"
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="Precio Total"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.movement_number} - {self.product.description} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Generar número de movimiento si es nuevo
        if not self.movement_number:
            last_movement = Movement.objects.order_by('-id').first()
            last_number = int(last_movement.movement_number.split('-')[1]) if last_movement else 0
            self.movement_number = f"MOV-{last_number + 1:05d}"
        
        # Calcular precio total
        self.total_price = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)
        
        # Actualizar stock del producto
        product = self.product
        if self.movement_type.is_entry:
            product.current_stock += self.quantity
        else:
            product.current_stock -= self.quantity
        product.save()