# libros/views.py
from django.shortcuts import render, redirect
from .forms import AsientoDiarioForm
# Aún no usaremos los otros modelos aquí, pero los necesitaremos pronto
from .models import MovimientoContable, Cuenta, AsientoDiario

def home(request):
    # Esta vista por ahora solo muestra la página.
    # En el futuro, aquí puedes agregar lógica para mostrar resúmenes o estadísticas.
    return render(request, 'libros/home.html')

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

# Agrega esta nueva vista:
def lista_cuentas(request):
    # 1. Obtiene todos los objetos 'Cuenta' de la base de datos
    cuentas = Cuenta.objects.all()
    # 2. Pasa los datos a la plantilla a través de un diccionario de contexto
    context = {
        'cuentas': cuentas
    }
    # 3. Renderiza el archivo HTML con los datos
    return render(request, 'libros/lista_cuentas.html', context)

# Agrega esta nueva vista para el Libro Diario:
def libro_diario(request):
    # 1. Obtiene todos los asientos, ordenados por fecha.
    # El prefetch_related('movimientos__cuenta') es una optimización para
    # cargar todos los datos relacionados de una sola vez.
    asientos = AsientoDiario.objects.prefetch_related('movimientos__cuenta').order_by('fecha')

    context = {
        'asientos': asientos
    }
    return render(request, 'libros/libro_diario.html', context)

def libro_mayor(request):
    # Obtiene todas las cuentas que tienen al menos un movimiento contable.
    cuentas_con_movimientos = Cuenta.objects.filter(movimientocontable__isnull=False).distinct().order_by('codigo')

    # Procesaremos los datos para que sea más fácil en la plantilla
    datos_mayor = []
    for cuenta in cuentas_con_movimientos:
        movimientos = cuenta.movimientocontable_set.all().order_by('asiento_diario__fecha')
        saldo = 0
        movimientos_con_saldo = []
        for mov in movimientos:
            # Asumimos una naturaleza deudora (Activos, Gastos)
            # Una lógica completa necesitaría saber la naturaleza de la cuenta.
            saldo += mov.debe - mov.haber
            movimientos_con_saldo.append({
                'fecha': mov.asiento_diario.fecha,
                'descripcion': mov.asiento_diario.descripcion,
                'debe': mov.debe,
                'haber': mov.haber,
                'saldo': saldo,
            })

        datos_mayor.append({
            'cuenta': cuenta,
            'movimientos': movimientos_con_saldo,
            'saldo_final': saldo,
        })

    context = {
        'datos_mayor': datos_mayor
    }
    return render(request, 'libros/libro_mayor.html', context)

def consultas(request):
    asientos_encontrados = None
    
    # Verificamos si el método es POST, lo que significa que el usuario envió el formulario
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        descripcion = request.POST.get('descripcion')
        
        # Empezamos con todos los asientos
        resultados = AsientoDiario.objects.all()
        
        # Aplicamos los filtros si los campos tienen valor
        if fecha_inicio and fecha_fin:
            resultados = resultados.filter(fecha__range=[fecha_inicio, fecha_fin])
        
        if descripcion:
            # Usamos __icontains para una búsqueda insensible a mayúsculas/minúsculas
            resultados = resultados.filter(descripcion__icontains=descripcion)
        
        asientos_encontrados = resultados.order_by('-fecha')

    context = {
        'asientos': asientos_encontrados
    }
    return render(request, 'libros/consultas.html', context)