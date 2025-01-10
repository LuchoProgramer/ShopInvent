from django.shortcuts import render, redirect
from django.contrib import messages
from django_tenants.utils import tenant_context
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from decimal import Decimal
from .services import crear_factura, asignar_pagos_a_factura, obtener_o_crear_cliente
from inventarios.services.validacion_inventario_service import ValidacionInventarioService
from RegistroTurnos.models import RegistroTurno
from facturacion.models import Carrito, Impuesto
from facturacion.forms import ImpuestoForm

@transaction.atomic
def generar_factura(request):
    tenant = request.tenant  # Obtener el tenant actual
    if request.method == 'POST':
        print(f"POST request para generar factura en tenant {tenant.schema_name}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Obtener los datos del formulario
                cliente_id = request.POST.get('cliente_id')
                identificacion = request.POST.get('identificacion')

                if not cliente_id and not identificacion:
                    return JsonResponse({'error': 'Debes seleccionar un cliente o ingresar los datos de un nuevo cliente.'}, status=400)

                # Filtrar clientes dentro del tenant
                data_cliente = {
                    'tipo_identificacion': request.POST.get('tipo_identificacion'),
                    'razon_social': request.POST.get('razon_social'),
                    'direccion': request.POST.get('direccion'),
                    'telefono': request.POST.get('telefono'),
                    'email': request.POST.get('email')
                }
                cliente = obtener_o_crear_cliente(cliente_id, identificacion, data_cliente, tenant)

                usuario = request.user
                turno_activo = RegistroTurno.objects.filter(
                    usuario=usuario, fin_turno__isnull=True, sucursal__empresa=tenant
                ).select_related('sucursal').first()

                if not turno_activo:
                    return JsonResponse({'error': 'No tienes un turno activo.'}, status=400)

                sucursal = turno_activo.sucursal

                # Obtener carrito dentro del tenant
                carrito_items = Carrito.objects.filter(turno=turno_activo).select_related('producto', 'presentacion')

                if not carrito_items.exists():
                    return JsonResponse({'error': 'El carrito está vacío. No se puede generar una factura.'}, status=400)

                # Verificar inventario
                for item in carrito_items:
                    if not ValidacionInventarioService.validar_inventario(item.producto, item.presentacion, item.cantidad):
                        return JsonResponse({'error': f'No hay suficiente inventario para {item.producto.nombre}.'}, status=400)

                # Crear factura dentro del tenant
                factura = crear_factura(cliente, sucursal, usuario, carrito_items, tenant)

                # Procesar pagos
                metodos_pago = request.POST.getlist('metodos_pago[]')
                montos_pago = [Decimal(monto) for monto in request.POST.getlist('montos_pago[]')]

                if sum(montos_pago) != factura.total_con_impuestos:
                    return JsonResponse({'error': 'El total pagado no coincide con el total de la factura.'}, status=400)

                asignar_pagos_a_factura(factura, metodos_pago, montos_pago)

                # Generar PDF en el contexto del tenant
                with tenant_context(tenant):
                    pdf_url = generar_pdf_factura_y_guardar(factura)

                carrito_items.delete()

                return JsonResponse({'success': True, 'pdf_url': pdf_url, 'redirect_url': reverse('ventas:inicio_turno', args=[turno_activo.id])})

            except Exception as e:
                return JsonResponse({'error': f'Ocurrió un error: {str(e)}'}, status=500)

    else:
        # Manejo de GET
        clientes = Cliente.objects.filter(empresa=tenant)  # Filtrar clientes por tenant
        carrito_items = obtener_carrito(request.user).select_related('producto')
        total_factura = sum(item.subtotal() for item in carrito_items)

        return render(request, 'facturacion/generar_factura.html', {
            'clientes': clientes,
            'total_factura': total_factura,
        })

def crear_impuesto(request):
    with tenant_context(request.tenant):
        # Cuando estamos en el contexto del tenant, no es necesario pasar empresa explícitamente
        if request.method == 'POST':
            form = ImpuestoForm(request.POST)
            if form.is_valid():
                # El campo 'empresa' será asignado automáticamente gracias al tenant_context
                impuesto = form.save()
                messages.success(request, 'Impuesto creado correctamente.')
                return redirect('facturacion:lista_impuestos')
            else:
                messages.error(request, 'Corrige los errores en el formulario.')
        else:
            form = ImpuestoForm()

    return render(request, 'facturacion/crear_impuesto.html', {'form': form})



def lista_impuestos(request):
    # Usar tenant_context para asegurar que la consulta se ejecute dentro del contexto del tenant adecuado
    with tenant_context(request.tenant):
        # No necesitamos obtener la empresa manualmente porque el tenant ya nos da el contexto correcto
        impuestos = Impuesto.objects.all()  # Traemos todos los impuestos del tenant actual

    return render(request, 'facturacion/lista_impuestos.html', {'impuestos': impuestos})
