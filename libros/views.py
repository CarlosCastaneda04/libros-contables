# libros/views.py
from django.shortcuts import render, redirect, get_object_or_404 
from django.db import transaction # Importamos transaction para seguridad
from django.http import JsonResponse
from django.db.models import Q
from .forms import AsientoDiarioForm
from django.db.models import Sum
from django.db.models import Max, IntegerField
from django.db.models.functions import Coalesce, Cast
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import openpyxl
# Aún no usaremos los otros modelos aquí, pero los necesitaremos pronto
from .models import MovimientoContable, Cuenta, AsientoDiario, Empresa

def home(request):
    # Obtenemos todas las empresas de la base de datos
    empresas = Empresa.objects.all()
    context = {
        'empresas': empresas
    }
    return render(request, 'libros/home.html', context)

def eliminar_asiento(request, asiento_id):
    # Usamos un método POST por seguridad para acciones destructivas
    if request.method == 'POST':
        # Buscamos el asiento, si no existe, dará un error 404
        asiento = get_object_or_404(AsientoDiario, pk=asiento_id)

        # Guardamos el ID de la empresa ANTES de borrar el asiento
        empresa_id = asiento.empresa.id

        # Eliminamos el asiento (y sus movimientos gracias a on_delete=CASCADE)
        asiento.delete()

        # Redirigimos de vuelta al libro diario de la empresa correcta
        return redirect('libro_diario', empresa_id=empresa_id)

    # Si alguien intenta acceder a la URL por GET, lo redirigimos al inicio
    return redirect('home')

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

# --- VISTA PARA GENERAR PDF ---
def libro_diario_pdf(request, empresa_id):
    # La lógica para obtener los datos es la misma que en la vista normal
    empresa = Empresa.objects.get(pk=empresa_id)
    asientos = AsientoDiario.objects.filter(empresa=empresa).order_by('fecha').prefetch_related('movimientos__cuenta')
    gran_total = MovimientoContable.objects.filter(asiento_diario__in=asientos).aggregate(
        total_debe=Sum('debe'), total_haber=Sum('haber')
    )
    context = {
        'asientos': asientos,
        'empresa': empresa,
        'gran_total_debe': gran_total['total_debe'] or 0,
        'gran_total_haber': gran_total['total_haber'] or 0,
        'is_for_pdf': True
    }

    # Renderizamos la plantilla HTML a una cadena de texto
    html_string = render_to_string('libros/libro_diario.html', context)

    # Usamos WeasyPrint para convertir el HTML a PDF
    pdf = HTML(string=html_string).write_pdf()

    # Creamos una respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="libro_diario_{empresa.nombre}.pdf"'
    return response

# --- VISTA PARA GENERAR EXCEL ---
def libro_diario_excel(request, empresa_id):
    # Obtenemos los datos de nuevo
    empresa = Empresa.objects.get(pk=empresa_id)
    asientos = AsientoDiario.objects.filter(empresa=empresa).order_by('fecha').prefetch_related('movimientos__cuenta')

    # Creamos un libro de Excel en memoria
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Libro Diario"

    # Escribimos los encabezados
    ws.append(['Fecha', 'Numero', 'Codigo', 'Descripcion', 'Debe', 'Haber'])

    # Escribimos los datos de cada asiento y movimiento
    for asiento in asientos:
        ws.append([asiento.fecha, asiento.numero_asiento, '', asiento.descripcion, '', ''])
        for movimiento in asiento.movimientos.all():
            ws.append(['', '', movimiento.cuenta.codigo, movimiento.cuenta.nombre, movimiento.debe, movimiento.haber])

    # Creamos la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="libro_diario_{empresa.nombre}.xlsx"'

    # Guardamos el libro de Excel en la respuesta
    wb.save(response)
    return response

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