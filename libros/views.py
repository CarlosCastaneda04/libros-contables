# libros/views.py
from django.shortcuts import render, redirect
from django.db import transaction # Importamos transaction para seguridad
from django.http import JsonResponse
from django.db.models import Q
from .forms import AsientoDiarioForm
from django.db.models import Sum
from django.db.models import Max, IntegerField
from django.db.models.functions import Coalesce, Cast
# Aún no usaremos los otros modelos aquí, pero los necesitaremos pronto
from .models import MovimientoContable, Cuenta, AsientoDiario, Empresa
from django.shortcuts import render, get_object_or_404

def home(request):
    # Obtenemos todas las empresas de la base de datos
    empresas = Empresa.objects.all()
    context = {
        'empresas': empresas
    }
    return render(request, 'libros/home.html', context)

def buscar_cuentas(request):
    # Obtenemos el término de búsqueda que nos envía el JavaScript
    term = request.GET.get('term', '')
    # Filtramos las cuentas
    cuentas = Cuenta.objects.filter(
        Q(codigo__istartswith=term) | Q(nombre__icontains=term)
    )[:10] # Usamos Q para buscar por código O por nombre. Limitamos a 10 resultados.

    resultados = []
    for cuenta in cuentas:
        resultados.append({
            'id': cuenta.codigo, # El valor que se guardará
            'text': f"{cuenta.codigo} - {cuenta.nombre}" # El texto que verá el usuario
        })

    return JsonResponse(resultados, safe=False)

def siguiente_numero_asiento(request, empresa_id):
    try:
        # Contamos cuántos asientos ya existen para esa empresa
        conteo = AsientoDiario.objects.filter(empresa__id=empresa_id).count()
        # El siguiente número es el conteo + 1
        siguiente_numero = conteo + 1
        # Devolvemos el número en formato JSON
        return JsonResponse({'siguiente_numero': siguiente_numero})
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)

# libros/views.py
from django.shortcuts import render, redirect
from django.db import transaction
from .forms import AsientoDiarioForm
from .models import MovimientoContable, Cuenta, AsientoDiario

# libros/views.py
@transaction.atomic
def crear_asiento(request):
    if request.method == 'POST':
        # Simplemente procesamos los datos que llegan
        form = AsientoDiarioForm(request.POST)
        if form.is_valid():
            asiento = form.save()

            # La lógica para guardar los movimientos no cambia
            indices = set()
            for key in request.POST:
                if key.startswith('movimientos-'):
                    indices.add(key.split('-')[1])

            for i in sorted(indices, key=int):
                cuenta_codigo = request.POST.get(f'movimientos-{i}-cuenta')
                debe = request.POST.get(f'movimientos-{i}-debe', 0)
                haber = request.POST.get(f'movimientos-{i}-haber', 0)

                if cuenta_codigo and (float(debe) > 0 or float(haber) > 0):
                    cuenta_obj = Cuenta.objects.get(pk=cuenta_codigo)
                    MovimientoContable.objects.create(
                        asiento_diario=asiento,
                        cuenta=cuenta_obj,
                        debe=debe,
                        haber=haber
                    )

            return redirect('libro_diario', empresa_id=asiento.empresa.id)
    else:
        # Para una carga inicial, solo creamos un formulario vacío
        form = AsientoDiarioForm()

    return render(request, 'libros/crear_asiento.html', {'form': form})


# Agrega esta nueva vista:
from django.shortcuts import render
from django.db import connection # ¡Asegúrate de importar 'connection'!
# from .models import Cuenta # Ya no es necesario para esta vista específica

# ... (tus otras vistas) ...

def lista_cuentas(request):
    # Creamos una lista vacía para guardar los resultados
    cuentas_list = []

    # Usamos una consulta SQL directa para evitar el ORM
    with connection.cursor() as cursor:
        # Ejecutamos tu consulta exacta
        cursor.execute("SELECT codigo, nombre, nivel, elemento, rubro FROM public.libros_cuenta ORDER BY codigo")

        # Recorremos cada fila que nos devuelve la base de datos
        for row in cursor.fetchall():
            # Creamos un diccionario para cada fila y lo agregamos a nuestra lista
            cuentas_list.append({
                'codigo': row[0],
                'nombre': row[1],
                'nivel':  row[2],
                'elemento': row[3],
                'rubro': row[4],
            })

    context = {
        'cuentas': cuentas_list
    }
    return render(request, 'libros/lista_cuentas.html', context)

# Agrega esta nueva vista para el Libro Diario:
def libro_diario(request, empresa_id):
    try:
        empresa = Empresa.objects.get(pk=empresa_id)
    except Empresa.DoesNotExist:
        return redirect('home')

    # Obtenemos los asientos de la empresa seleccionada
    asientos = AsientoDiario.objects.filter(empresa=empresa).order_by('fecha').prefetch_related('movimientos__cuenta')

    # --- INICIO DE LA NUEVA LÓGICA ---
    # Calculamos el total general de todos los movimientos de estos asientos
    gran_total = MovimientoContable.objects.filter(asiento_diario__in=asientos).aggregate(
        total_debe=Sum('debe'),
        total_haber=Sum('haber')
    )
    # --- FIN DE LA NUEVA LÓGICA ---

    context = {
        'asientos': asientos,
        'empresa': empresa,
        'gran_total_debe': gran_total['total_debe'] or 0,
        'gran_total_haber': gran_total['total_haber'] or 0
    }
    return render(request, 'libros/libro_diario.html', context)

def lista_empresas(request):
    empresas = Empresa.objects.all()
    return render(request, 'libros/lista_empresas.html', {'empresas': empresas})

def balance_comprobacion(request, empresa_id=None):
    empresas = Empresa.objects.all()
    empresa_seleccionada = None
    datos_balance = []
    total_deudor = 0
    total_acreedor = 0
    
    # Si se proporcionó un ID de empresa
    if empresa_id:
        empresa_seleccionada = get_object_or_404(Empresa, id=empresa_id)
        
        movimientos_empresa = MovimientoContable.objects.filter(asiento_diario__empresa=empresa_seleccionada)
        
        cuentas_con_movimientos = Cuenta.objects.filter(
            movimientocontable__in=movimientos_empresa
        ).distinct().order_by('codigo')

        for cuenta in cuentas_con_movimientos:
            totales = movimientos_empresa.filter(cuenta=cuenta).aggregate(
                debe=Sum('debe'),
                haber=Sum('haber')
            )
            debe_total = totales['debe'] or 0
            haber_total = totales['haber'] or 0
            
            saldo_deudor = max(0, debe_total - haber_total)
            saldo_acreedor = max(0, haber_total - debe_total)

            total_deudor += debe_total
            total_acreedor += haber_total

            datos_balance.append({
                'cuenta': cuenta,
                'debe': debe_total,
                'haber': haber_total,
                'saldo_deudor': saldo_deudor,
                'saldo_acreedor': saldo_acreedor
            })

    contexto = {
        'empresas': empresas,
        'empresa_seleccionada': empresa_seleccionada,
        'datos_balance': datos_balance,
        'total_deudor': total_deudor,
        'total_acreedor': total_acreedor,
    }

    return render(request, 'libros/balance_comprobacion.html', contexto)




def libro_mayor(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # Obtener TODAS las empresas para el selector
    todas_empresas = Empresa.objects.all()
    
    # Obtener parámetros del filtro
    cuenta_codigo = request.GET.get('cuenta_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Obtener TODAS las cuentas disponibles
    cuentas = Cuenta.objects.all()
    
    # Base query - filtrar por empresa
    movimientos = MovimientoContable.objects.filter(
        asiento_diario__empresa=empresa
    ).select_related('asiento_diario', 'cuenta')
    
    # Aplicar filtros
    if cuenta_codigo:
        movimientos = movimientos.filter(cuenta__codigo=cuenta_codigo)
    
    if fecha_inicio:
        movimientos = movimientos.filter(asiento_diario__fecha__gte=fecha_inicio)
    
    if fecha_fin:
        movimientos = movimientos.filter(asiento_diario__fecha__lte=fecha_fin)
    
    # Agrupar movimientos por cuenta
    datos_mayor = []
    
    # Obtener cuentas únicas que tienen movimientos con los filtros aplicados
    cuentas_con_movimientos = Cuenta.objects.filter(
        movimientocontable__in=movimientos
    ).distinct()
    
    for cuenta in cuentas_con_movimientos:
        movimientos_cuenta = movimientos.filter(cuenta=cuenta).order_by('asiento_diario__fecha', 'id')
        
        saldo_acumulado = 0
        movimientos_con_saldo = []
        
        for mov in movimientos_cuenta:
            saldo_acumulado += mov.debe - mov.haber
            movimientos_con_saldo.append({
                'fecha': mov.asiento_diario.fecha,
                'descripcion': mov.asiento_diario.descripcion,
                'debe': mov.debe,
                'haber': mov.haber,
                'saldo': saldo_acumulado
            })
        
        datos_mayor.append({
            'cuenta': cuenta,
            'movimientos': movimientos_con_saldo,
            'saldo_final': saldo_acumulado
        })
    
    context = {
        'empresa': empresa,
        'todas_empresas': todas_empresas,  # Nuevo: todas las empresas para el selector
        'cuentas': cuentas,
        'datos_mayor': datos_mayor,
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