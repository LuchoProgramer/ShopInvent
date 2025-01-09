# facturacion/urls.py
from django.urls import path
from . import views

app_name = 'facturacion'  # Usamos el namespace 'facturacion'

urlpatterns = [
    path('impuestos/', views.lista_impuestos, name='lista_impuestos'),
    path('impuestos/crear/', views.crear_impuesto, name='crear_impuesto'),
    # Otras rutas relacionadas con impuestos
]
