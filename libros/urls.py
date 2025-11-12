# libros/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_asiento, name='crear_asiento'),
    path('cuentas/', views.lista_cuentas, name='lista_cuentas'),
    path('libro-diario/<int:empresa_id>/', views.libro_diario, name='libro_diario'),
    path('consultas/', views.consultas, name='consultas'),
    path('buscar-cuentas/', views.buscar_cuentas, name='buscar_cuentas'),
    path('siguiente-asiento/<int:empresa_id>/', views.siguiente_numero_asiento, name='siguiente_asiento'),
    path('libro-diario/<int:empresa_id>/pdf/', views.libro_diario_pdf, name='libro_diario_pdf'),
    path('libro-diario/<int:empresa_id>/excel/', views.libro_diario_excel, name='libro_diario_excel'),
    path('asiento/eliminar/<int:asiento_id>/', views.eliminar_asiento, name='eliminar_asiento'),
    path('empresa/agregar/', views.agregar_empresa, name='agregar_empresa'),
    path('empresa/eliminar/<int:empresa_id>/', views.eliminar_empresa, name='eliminar_empresa'),
    path('balance-comprobacion/', views.balance_comprobacion, name='balance_comprobacion_general'),
    path('libro-mayor/', views.libro_mayor, name='libro_mayor_general'),
    path('libro-mayor/<int:empresa_id>/', views.libro_mayor, name='libro_mayor'),
    path('balance-comprobacion/<int:empresa_id>/', views.balance_comprobacion, name='balance_comprobacion'),
    path('empresas/', views.lista_empresas, name='lista_empresas'),
    # --- INICIO DE NUEVAS URLS PARA LA ACTIVIDAD III ---

    # 1. Página del submenú de reportes financieros
    path('reportes-financieros/', views.reportes_financieros, name='reportes_financieros'),
    
    # 2. El nuevo Balance de Comprobación (usaremos un nombre de vista diferente)
    path('nuevo-balance-comprobacion/<int:empresa_id>/', views.nuevo_balance_comprobacion, name='nuevo_balance_comprobacion'),
    
    # 3. El Estado de Resultados
    path('estado-resultados/<int:empresa_id>/', views.estado_resultados, name='estado_resultados'),
    
    # 4. El Balance General
    path('balance-general/<int:empresa_id>/', views.balance_general, name='balance_general'),
    
    # --- FIN DE NUEVAS URLS ---
]
    
    
    
    
