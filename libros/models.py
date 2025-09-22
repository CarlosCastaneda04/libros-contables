from django.db import models
from django.db.models import Q, CheckConstraint

# 1. Modelo para la tabla 'Empresa'
class Empresa(models.Model):
    # Django crea un 'id' SERIAL PRIMARY KEY automáticamente.
    nombre = models.CharField(max_length=255, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# 2. Modelo para la tabla 'Cuenta'
class Cuenta(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    nombre = models.CharField(max_length=255)
    # La relación recursiva. ON DELETE RESTRICT equivale a PROTECT en Django.
    codigo_padre = models.ForeignKey(
        'self', 
        on_delete=models.PROTECT,
        null=True, 
        blank=True,
        related_name='hijos'
    )

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        ordering = ['codigo']

# 3. Modelo para la tabla 'AsientoDiario'
class AsientoDiario(models.Model):
    # El 'id' se crea automáticamente.
    numero_asiento = models.CharField(max_length=50, unique=True)
    fecha = models.DateField()
    descripcion = models.TextField()
    # Django maneja el '_id' automáticamente al crear la relación.
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.numero_asiento}: {self.descripcion}"

    class Meta:
        # Nombres para el panel de admin de Django.
        verbose_name = "Asiento de Diario"
        verbose_name_plural = "Asientos de Diario"

# 4. Modelo para la tabla 'MovimientoContable'
class MovimientoContable(models.Model):
    # El 'id' se crea automáticamente.
    asiento_diario = models.ForeignKey(AsientoDiario, on_delete=models.CASCADE, related_name='movimientos')
    cuenta = models.ForeignKey(Cuenta, to_field='codigo', on_delete=models.PROTECT, db_column='cuenta_codigo')
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Movimiento de {self.cuenta.nombre} en Asiento {self.asiento_diario.id}"

    class Meta:
        # Así se replica la restricción CHECK de SQL en Django.
        constraints = [
            CheckConstraint(
                check=Q(debe__gte=0) & Q(haber__gte=0),
                name='montos_no_negativos'
            )
        ]
        verbose_name = "Movimiento Contable"
        verbose_name_plural = "Movimientos Contables"