# libros/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_asiento, name='crear_asiento'),
    path('cuentas/', views.lista_cuentas, name='lista_cuentas'),    
    path('libro-diario/<int:empresa_id>/', views.libro_diario, name='libro_diario'),
    path('libro-mayor/', views.libro_mayor, name='libro_mayor'),
    path('consultas/', views.consultas, name='consultas'),
    path('buscar-cuentas/', views.buscar_cuentas, name='buscar_cuentas'),

]