from django.contrib import admin
from .models import Empresa, Cuenta, AsientoDiario, MovimientoContable

# Registrar cada modelo para que aparezca en el sitio de admin
admin.site.register(Empresa)
admin.site.register(Cuenta)
admin.site.register(AsientoDiario)
admin.site.register(MovimientoContable)