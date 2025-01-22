from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .forms import ProveedorForm, DetalleCompraForm, CompraForm
from .models import Proveedor, Compra, DetalleCompra
from django_tenants.utils import tenant_context
from django.forms import inlineformset_factory
from decimal import Decimal, ROUND_HALF_UP, getcontext
from django.core.exceptions import ValidationError
from facturacion.models import Impuesto


def crear_proveedor(request):
    with tenant_context(request.tenant):  # Asegura que el proveedor se asocia al tenant actual
        if request.method == 'POST':
            form = ProveedorForm(request.POST)
            if form.is_valid():
                proveedor = form.save(commit=False)
                proveedor.empresa = request.tenant  # Asociar al tenant actual (empresa)
                proveedor.save()
                messages.success(request, f'Proveedor "{proveedor.nombre}" creado exitosamente.')
                return redirect('proveedores:detalle', proveedor_id=proveedor.pk)
            else:
                messages.error(request, 'Corrige los errores en el formulario.')
        else:
            form = ProveedorForm()

        return render(request, 'proveedores/crear_editar_proveedor.html', {'form': form})



def editar_proveedor(request, proveedor_id):
    with tenant_context(request.tenant):
        proveedor = get_object_or_404(Proveedor, id=proveedor_id, empresa=request.tenant)
        if request.method == 'POST':
            form = ProveedorForm(request.POST, instance=proveedor)
            if form.is_valid():
                form.save()
                messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado exitosamente.')
                return redirect('proveedores:detalle', proveedor_id=proveedor.pk)
            else:
                print("Errores del formulario:", form.errors)
                messages.error(request, 'Corrige los errores en el formulario.')
        else:
            form = ProveedorForm(instance=proveedor)

        return render(request, 'proveedores/crear_editar_proveedor.html', {'form': form, 'proveedor': proveedor})


def detalle_proveedor(request, proveedor_id):
    with tenant_context(request.tenant):
        proveedor = get_object_or_404(Proveedor, id=proveedor_id, empresa=request.tenant)
        context = {'proveedor': proveedor}
        return render(request, 'proveedores/detalle_proveedor.html', context)


def lista_proveedores(request):
    with tenant_context(request.tenant):  # Asegura que los proveedores se asocian al tenant actual
        proveedores = Proveedor.objects.all()  # Obtiene todos los proveedores asociados al tenant actual
    return render(request, 'proveedores/lista_proveedores.html', {'proveedores': proveedores})



def lista_compras(request):
    with tenant_context(request.tenant):
        compras = Compra.objects.all()  # Se asegura de obtener solo las compras del tenant actual
    return render(request, 'compras/lista_compras.html', {'compras': compras})

def crear_compra_con_productos(request):
    with tenant_context(request.tenant):
        DetalleCompraFormSet = inlineformset_factory(
            Compra, DetalleCompra, form=DetalleCompraForm, extra=1
        )

        impuesto_activo = Impuesto.objects.filter(activo=True).first()
        if not impuesto_activo:
            raise ValidationError("No hay un impuesto activo definido.")

        if request.method == 'POST':
            compra_form = CompraForm(request.POST)
            formset = DetalleCompraFormSet(request.POST, prefix='detalles')

            if compra_form.is_valid() and formset.is_valid():
                compra = compra_form.save(commit=False)
                compra.total_sin_impuestos = Decimal('0.00')
                compra.total_con_impuestos = Decimal('0.00')
                compra.save()

                total_sin_impuestos = Decimal('0.00')
                total_con_impuestos = Decimal('0.00')

                detalles = formset.save(commit=False)
                for detalle in detalles:
                    detalle.compra = compra

                    precio_unitario = Decimal(str(detalle.precio_unitario))
                    cantidad = Decimal(str(detalle.cantidad))

                    total_linea_sin_impuesto = precio_unitario * cantidad
                    total_linea_con_impuesto = total_linea_sin_impuesto + (
                        total_linea_sin_impuesto * (Decimal(str(impuesto_activo.porcentaje)) / Decimal('100'))
                    )

                    total_sin_impuestos += total_linea_sin_impuesto
                    total_con_impuestos += total_linea_con_impuesto

                    detalle.save()

                compra.total_sin_impuestos = total_sin_impuestos.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                compra.total_con_impuestos = total_con_impuestos.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                compra.save()

                return redirect('compras:lista_compras')
            else:
                print('Errores en compra_form:', compra_form.errors)
                print('Errores en formset:')
                for form in formset:
                    print(form.errors)
        else:
            compra_form = CompraForm()
            formset = DetalleCompraFormSet(prefix='detalles')

    return render(request, 'compras/crear_compra_con_productos.html', {
        'compra_form': compra_form,
        'formset': formset,
        'impuesto_activo': impuesto_activo.porcentaje,
    })


def detalle_compra(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)
    with tenant_context(compra.sucursal.empresa):
        detalles = compra.detalles.all()
    return render(request, 'compras/detalle_compra.html', {'compra': compra, 'detalles': detalles})

