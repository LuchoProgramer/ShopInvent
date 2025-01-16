from django.shortcuts import render, redirect, get_object_or_404
from django_tenants.utils import tenant_context
from django.core.paginator import Paginator
from .models import Inventario
from core.models import Sucursal, Producto
from django.contrib import messages
from .forms import InventarioForm

def seleccionar_sucursal(request):
    usuario = request.user
    
    # Obtener el tenant del usuario
    tenant = usuario.tenant  # Ajusta esto según cómo relaciones los usuarios con los tenants
    
    with tenant_context(tenant):
        sucursales = usuario.sucursales.all()  # Se ejecuta dentro del esquema correcto
    
    if request.method == 'POST':
        sucursal_id = request.POST.get('sucursal_id')
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal_id)

    return render(request, 'inventarios/seleccionar_sucursal.html', {'sucursales': sucursales})



def ver_inventario(request, sucursal_id):
    # Obtener la sucursal seleccionada, filtrando por el tenant activo
    sucursal = get_object_or_404(Sucursal, id=sucursal_id, empresa=request.tenant)  # Suponiendo que `empresa` es un ForeignKey a `Empresa`

    # Obtener el inventario para esa sucursal, con el producto relacionado precargado
    inventarios = Inventario.objects.filter(sucursal=sucursal).select_related('producto')

    # Paginación del inventario, 10 elementos por página
    paginator = Paginator(inventarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventarios/ver_inventario.html', {
        'sucursal': sucursal,
        'inventarios': page_obj,  # Cambié 'inventario' a 'inventarios' y añadí paginación
    })


def agregar_producto_inventario(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        sucursal_id = request.POST.get('sucursal_id')
        cantidad = request.POST.get('cantidad')

        # Validar que 'cantidad' no sea nulo ni vacío
        if not cantidad:
            messages.error(request, 'La cantidad es requerida.')
            return redirect('inventarios:agregar_producto_inventario')

        # Intentar convertir 'cantidad' a entero y manejar el error si no es válido
        try:
            cantidad = int(cantidad)
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return redirect('inventarios:agregar_producto_inventario')

        # Filtrar las sucursales por el tenant actual
        sucursal = get_object_or_404(Sucursal, id=sucursal_id, empresa=request.tenant)

        # Ahora puedes proceder a guardar la cantidad en el inventario
        try:
            inventario, created = Inventario.objects.get_or_create(
                producto_id=producto_id, 
                sucursal=sucursal,  # Usamos el objeto Sucursal en lugar de solo el ID
                defaults={'cantidad': cantidad}
            )
            if not created:
                inventario.cantidad += cantidad  # Sumar cantidad si ya existe el producto
                inventario.save()

            messages.success(request, 'Producto agregado al inventario.')
        except Exception as e:
            messages.error(request, f'Error al agregar el producto: {e}')
        
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal_id)

    else:
        # Aquí puedes cargar cualquier dato necesario para el formulario
        productos = Producto.objects.all()
        sucursales = Sucursal.objects.filter(empresa=request.tenant)  # Filtramos las sucursales por el tenant actual
        return render(request, 'inventarios/agregar_producto.html', {'productos': productos, 'sucursales': sucursales})


def ajustar_inventario(request, producto_id, sucursal_id):
    # Asegúrate de que la sucursal esté asociada al tenant correcto
    sucursal = get_object_or_404(Sucursal, id=sucursal_id, empresa=request.tenant)
    producto = get_object_or_404(Producto, id=producto_id)

    # Asegúrate de que el inventario esté asociado a la sucursal y al tenant
    inventario = get_object_or_404(Inventario, producto=producto, sucursal=sucursal)

    if request.method == 'POST':
        nueva_cantidad = request.POST.get('nueva_cantidad')

        # Validar que la nueva cantidad es un número entero válido
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa")
        except ValueError:
            # Si la cantidad no es válida, podrías mostrar un mensaje de error
            return render(request, 'inventarios/ajustar_inventario.html', {
                'inventario': inventario,
                'producto': producto,
                'sucursal': sucursal,
                'error': 'La cantidad debe ser un número entero válido y no negativo.'
            })

        # Actualizamos la cantidad en el inventario
        inventario.cantidad = nueva_cantidad
        inventario.save()

        # Redirigir al inventario de la sucursal, pasando el sucursal_id correctamente
        messages.success(request, 'Inventario ajustado correctamente.')
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal.id)

    return render(request, 'inventarios/ajustar_inventario.html', {
        'inventario': inventario,
        'producto': producto,
        'sucursal': sucursal
    })


from django.shortcuts import get_object_or_404, redirect, render
from .models import Transferencia, Inventario, MovimientoInventario, Producto, Sucursal
from .forms import TransferenciaForm
from django.contrib import messages

def crear_transferencia(request):
    if request.method == 'POST':
        form = TransferenciaForm(request.POST)
        if form.is_valid():
            transferencia = form.save(commit=False)

            # Asegurarse de que las sucursales de origen y destino estén asociadas al tenant actual
            sucursal_origen = get_object_or_404(Sucursal, id=transferencia.sucursal_origen.id, empresa=request.tenant)
            sucursal_destino = get_object_or_404(Sucursal, id=transferencia.sucursal_destino.id, empresa=request.tenant)

            # Verificar si hay suficiente inventario en la sucursal de origen
            inventario_origen = get_object_or_404(Inventario, sucursal=sucursal_origen, producto=transferencia.producto)

            if inventario_origen.cantidad < transferencia.cantidad:
                form.add_error('cantidad', 'No hay suficiente inventario en la sucursal de origen.')
            else:
                # Actualizar inventario de origen
                inventario_origen.cantidad -= transferencia.cantidad
                inventario_origen.save()

                # Obtener o crear inventario en la sucursal destino
                inventario_destino, created = Inventario.objects.get_or_create(
                    sucursal=sucursal_destino,
                    producto=transferencia.producto,
                    defaults={'cantidad': 0}  # Asignar cantidad inicial si no existe
                )

                if not created:
                    inventario_destino.cantidad += transferencia.cantidad
                else:
                    inventario_destino.cantidad = transferencia.cantidad
                
                inventario_destino.save()

                # Guardar la transferencia
                transferencia.save()

                # Registrar movimiento de inventario
                MovimientoInventario.objects.create(
                    sucursal=sucursal_origen,
                    producto=transferencia.producto,
                    cantidad_transferida=transferencia.cantidad,
                    tipo_movimiento='Transferencia',
                    fecha=transferencia.fecha,
                )
                MovimientoInventario.objects.create(
                    sucursal=sucursal_destino,
                    producto=transferencia.producto,
                    cantidad_transferida=transferencia.cantidad,
                    tipo_movimiento='Transferencia',
                    fecha=transferencia.fecha,
                )

                messages.success(request, 'Transferencia realizada correctamente.')
                return redirect('inventarios:lista_transferencias')
    else:
        form = TransferenciaForm()

    return render(request, 'inventarios/crear_transferencia.html', {'form': form})


def lista_transferencias(request):
    transferencias = Transferencia.objects.filter(sucursal_origen__empresa=request.tenant, sucursal_destino__empresa=request.tenant)
    return render(request, 'inventarios/lista_transferencias.html', {'transferencias': transferencias})

def lista_movimientos_inventario(request):
    movimientos = MovimientoInventario.objects.filter(sucursal__empresa=request.tenant).order_by('-fecha')
    return render(request, 'inventarios/lista_movimientos_inventario.html', {'movimientos': movimientos})




def agregar_inventario_manual(request):
    # Obtener la sucursal desde el query string y filtrarla por el tenant actual
    sucursal_id = request.GET.get('sucursal')  # Obtener la sucursal desde el query string
    sucursal = get_object_or_404(Sucursal, id=sucursal_id, empresa=request.tenant)  # Filtrar por el tenant actual

    if request.method == 'POST':
        # Pasar el tenant al formulario para filtrar productos y sucursales
        form = InventarioForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            # Obtener o crear el inventario para el producto en esa sucursal
            inventario, created = Inventario.objects.get_or_create(
                producto=form.cleaned_data['producto'],
                sucursal=sucursal,
                defaults={'cantidad': form.cleaned_data['cantidad']}
            )
            if not created:
                inventario.cantidad += form.cleaned_data['cantidad']  # Si ya existe, sumar la cantidad
            inventario.save()

            # Redirigir a la vista de inventario de esa sucursal
            return redirect('inventarios:ver_inventario', sucursal_id=sucursal.id)
    else:
        # Crear el formulario con el tenant actual
        form = InventarioForm(tenant=request.tenant)

    return render(request, 'inventarios/agregar_inventario_manual.html', {
        'form': form, 
        'sucursal': sucursal
    })