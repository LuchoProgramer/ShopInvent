from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Sucursal, Producto, Categoria, Presentacion
from .forms import SucursalForm, ProductoForm, CategoriaForm, PresentacionMultipleForm
from django.contrib.auth.decorators import login_required
from django_tenants.utils import tenant_context  # Importante para cambiar el contexto al tenant actual
from django.http import JsonResponse
from django.forms import inlineformset_factory


# Home 
def home(request):
    # Aquí puedes incluir cualquier dato adicional si lo necesitas
    return render(request, 'core/home.html')

# Lista de sucursales
#@login_required
def lista_sucursales(request):
    with tenant_context(request.tenant):
        sucursales = Sucursal.objects.all()  # Esto ahora solo devuelve las sucursales del tenant actual
    return render(request, 'core/lista_sucursales.html', {'sucursales': sucursales})


#@login_required
def crear_sucursal(request):
    with tenant_context(request.tenant):
        print(f"request.tenant en crear_sucursal: {request.tenant}") #Debug en la vista
        if request.method == 'POST':
            form = SucursalForm(request.POST, empresa=request.tenant)
            if form.is_valid():
                sucursal = form.save()
                messages.success(request, f'Sucursal "{sucursal.nombre}" creada exitosamente.')
                return redirect('core:detalle_sucursal', sucursal_id=sucursal.pk)
            else:
                print("Errores del formulario:", form.errors)
                messages.error(request, 'Corrige los errores en el formulario.')
        else:
            form = SucursalForm(empresa=request.tenant)
        return render(request, 'core/crear_editar_sucursal.html', {'form': form, 'sucursal': None, 'empresa':request.tenant})

#@login_required
def editar_sucursal(request, sucursal_id):
    with tenant_context(request.tenant):
        sucursal = get_object_or_404(Sucursal, pk=sucursal_id, empresa=request.tenant)
        if request.method == 'POST':
            form = SucursalForm(request.POST, instance=sucursal, empresa=request.tenant)
            if form.is_valid():
                form.save()
                messages.success(request, 'Sucursal actualizada exitosamente.')
                return redirect('core:detalle_sucursal', sucursal_id=sucursal.pk)
            else:
                print("Errores del formulario:", form.errors)
                messages.error(request, 'Corrige los errores en el formulario.')
        else:
            form = SucursalForm(instance=sucursal, empresa=sucursal.empresa)
        return render(request, 'core/crear_editar_sucursal.html', {'form': form, 'sucursal': sucursal, 'empresa':request.tenant})


def detalle_sucursal(request, sucursal_id):
    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)
    context = {'sucursal': sucursal}
    return render(request, 'core/detalle_sucursal.html', context) #Ruta a tu template.

# Eliminar sucursal
#@login_required
def eliminar_sucursal(request, sucursal_id):
    # Usamos tenant_context para asegurarnos de que la consulta se haga en el esquema del tenant actual
    with tenant_context(request.tenant):
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)

    if request.method == 'POST':
        sucursal.delete()
        messages.success(request, 'Sucursal eliminada exitosamente.')
        return redirect('core:lista_sucursales')  # Redirige a la lista de sucursales

    return render(request, 'core/eliminar_sucursal.html', {'sucursal': sucursal})


def agregar_producto(request):
    tenant = request.tenant  # Obtener el tenant actual
    producto = None

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, empresa=tenant)

        if form.is_valid():
            with tenant_context(tenant):  # Asegurar que el producto se guarde en el esquema correcto
                producto = form.save(commit=False)
                producto.empresa = tenant  # Asociar explícitamente el producto al tenant
                producto.save()

                if hasattr(form, 'save_m2m'):
                    form.save_m2m()

            messages.success(request, 'Producto agregado exitosamente.')
            return redirect('core:lista_productos')
    else:
        form = ProductoForm(empresa=tenant)

    return render(request, 'core/agregar_producto.html', {'form': form})



def lista_productos(request):
    # Verificar si el usuario tiene al menos una sucursal asociada
    if not request.user.sucursales.exists():
        # Redirigir o mostrar un mensaje si no tiene sucursales asociadas
        return redirect('core:sin_sucursal')  # Asumiendo que tienes una vista para este caso

    # Obtener la empresa asociada al usuario (tenant)
    empresa = request.user.sucursales.first().empresa

    # Obtener los productos de la empresa del usuario
    productos = Producto.objects.filter(empresa=empresa)

    # Verificar si el usuario tiene permiso para eliminar productos
    tiene_permiso = request.user.has_perm("core.delete_producto")
    
    # Recopilar la información de las presentaciones relacionadas
    for producto in productos:
        # Buscar la primera presentación asociada al producto y la sucursal correcta
        presentacion = producto.presentaciones.filter(sucursal__empresa=empresa).first()
        if presentacion:
            producto.presentacion_info = presentacion
        else:
            producto.presentacion_info = None
        
        # Asignar la sucursal asociada (si existe)
        producto.sucursal = producto.sucursales.filter(empresa=empresa).first()

    # Contexto con productos y permisos
    context = {
        'productos': productos,
        'tiene_permiso': tiene_permiso,
        'tenant': empresa  # Pasamos la empresa directamente
    }

    return render(request, 'core/lista_productos.html', context)


def sin_sucursal(request):
    return render(request, 'core/sin_sucursal.html')




def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    # Obtener la empresa (tenant) del usuario
    tenant = request.user.sucursales.first().empresa if request.user.sucursales.exists() else None

    if tenant:
        productos = Producto.objects.filter(categoria=categoria, empresa=tenant)
        
        # Para cada producto, obtener la primera presentación asociada a la empresa (tenant)
        for producto in productos:
            presentacion = producto.presentaciones.filter(sucursal__empresa=tenant).first()
            producto.presentacion_info = presentacion  # Guardamos la presentación asociada en un atributo del producto
    else:
        productos = []

    context = {
        'categoria': categoria,
        'productos': productos,
        'tenant': tenant
    }

    return render(request, 'core/productos_por_categoria.html', context)



def editar_producto(request, producto_id):
    tenant = request.tenant 

    with tenant_context(tenant):
        producto = get_object_or_404(Producto, id=producto_id, empresa=tenant) 

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto, empresa=tenant)
        if form.is_valid():
            with tenant_context(tenant):
                form.save()
            return redirect('core:lista_productos')
    else:
        form = ProductoForm(instance=producto, empresa=tenant)

    return render(request, 'core/editar_producto.html', {'form': form, 'producto': producto})


def ver_producto(request, producto_id):
    tenant = request.tenant

    with tenant_context(tenant):
        producto = get_object_or_404(Producto, id=producto_id, empresa=tenant)
        presentaciones = Presentacion.objects.filter(producto=producto, empresa=tenant)

    return render(request, 'core/ver_producto.html', {
        'producto': producto,
        'presentaciones': presentaciones,
        'tenant': tenant, # Pasar el tenant al template
    })


def agregar_categoria(request):
    tenant = request.tenant

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.empresa = tenant
            categoria.save()
            return redirect('core:lista_categorias')  # Redirigir a la lista de categorías
    else:
        form = CategoriaForm()

    return render(request, 'core/agregar_categoria.html', {'form': form})



def lista_categorias(request):
    tenant = request.tenant  # Obtém o tenant atual da requisição

    with tenant_context(tenant): # Garante que a consulta seja feita no esquema do tenant
        categorias = Categoria.objects.filter(empresa=tenant) # Filtra as categorias pelo tenant atual
        #Ou
        #categorias = Categoria.objects.all()

    return render(request, 'core/lista_categorias.html', {'categorias': categorias, 'tenant': tenant}) # Passa tenant para o template


# Presentaciones

# Crear un formset para Presentacion
PresentacionFormSet = inlineformset_factory(
    Producto, 
    Presentacion, 
    form=PresentacionMultipleForm, 
    extra=1,
    fields=['nombre_presentacion', 'cantidad', 'precio', 'sucursal']
)

def agregar_presentaciones_multiples(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, empresa=request.tenant)  # Aseguramos que el producto sea del tenant

    if request.method == 'POST':
        form = PresentacionMultipleForm(request.POST)
        if form.is_valid():
            sucursales = form.cleaned_data['sucursales']
            nombre_presentacion = form.cleaned_data['nombre_presentacion']

            # Almacenar errores si alguna presentación ya existe
            errores = []

            presentaciones_creadas = []  # Guardar las presentaciones que se crearon

            for sucursal in sucursales:
                # Verificar si la sucursal está asociada al tenant actual
                if sucursal.empresa != request.tenant:
                    errores.append(f"La sucursal {sucursal.nombre} no pertenece a tu empresa.")
                    continue  # Saltar esta iteración si no es del tenant

                # Verificar si ya existe la presentación en la misma sucursal
                if Presentacion.objects.filter(
                    producto=producto,
                    nombre_presentacion=nombre_presentacion,
                    sucursal=sucursal
                ).exists():
                    error = f'La presentación "{nombre_presentacion}" ya existe en {sucursal.nombre}.'
                    errores.append(error)
                    continue  # Saltar esta iteración si ya existe

                # Crear la nueva presentación si no existe
                nueva_presentacion = Presentacion(
                    producto=producto,
                    nombre_presentacion=nombre_presentacion,
                    cantidad=form.cleaned_data['cantidad'],
                    precio=form.cleaned_data['precio'],
                    sucursal=sucursal
                )
                nueva_presentacion.save()
                presentaciones_creadas.append(nueva_presentacion)

            # Si hubo errores, devolverlos como respuesta
            if errores:
                return JsonResponse({
                    'success': False,
                    'error': ' | '.join(errores)
                }, status=400)

            # Responder con las presentaciones creadas
            presentaciones_data = [
                {
                    'id': p.id,
                    'nombre_presentacion': p.nombre_presentacion,
                    'cantidad': p.cantidad,
                    'precio': p.precio,
                    'sucursal': p.sucursal.nombre
                }
                for p in presentaciones_creadas
            ]

            return JsonResponse({
                'success': True,
                'presentaciones': presentaciones_data
            })

        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # Lógica para el método GET
    presentaciones_existentes = Presentacion.objects.filter(producto=producto, sucursal__empresa=request.tenant)
    form = PresentacionMultipleForm()

    return render(request, 'core/agregar_presentaciones_multiples.html', {
        'form': form,
        'producto': producto,
        'presentaciones_existentes': presentaciones_existentes,
    })


def eliminar_presentacion(request, presentacion_id):
    if request.method == 'POST':
        try:
            presentacion = Presentacion.objects.get(id=presentacion_id, producto__empresa=request.tenant)
            presentacion.delete()
            return JsonResponse({'success': True})
        except Presentacion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Presentación no encontrada o no pertenece a tu empresa.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})
