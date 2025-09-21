# libros/views.py
from django.shortcuts import render, redirect
from .forms import AsientoDiarioForm
# Aún no usaremos los otros modelos aquí, pero los necesitaremos pronto
from .models import MovimientoContable, Cuenta

def crear_asiento(request):
    if request.method == 'POST':
        # Si el formulario fue enviado...
        form = AsientoDiarioForm(request.POST)
        if form.is_valid():
            # Si los datos son válidos, guarda el AsientoDiario
            asiento = form.save()
            # Aquí iría la lógica para guardar los MovimientoContable
            # Por ahora, solo redirigimos a otra página (que crearemos después)
            return redirect('home') # 'home' será el nombre de nuestra página principal
    else:
        # Si se accede a la página por primera vez, muestra un formulario vacío
        form = AsientoDiarioForm()

    return render(request, 'libros/crear_asiento.html', {'form': form})