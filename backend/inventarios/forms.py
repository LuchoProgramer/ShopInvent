from django import forms
from .models import Transferencia, Inventario
from core.models import Sucursal, Producto


class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['sucursal_origen', 'sucursal_destino', 'producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar sucursales por el tenant actual
        tenant = kwargs.get('tenant', None)  # Puedes pasar el tenant desde la vista o usar `request.tenant`
        if tenant:
            self.fields['sucursal_origen'].queryset = Sucursal.objects.filter(empresa=tenant)
            self.fields['sucursal_destino'].queryset = Sucursal.objects.filter(empresa=tenant)
        
        # Filtrar productos si es necesario
        # Puedes filtrar productos si también están asociados al tenant de alguna manera
        self.fields['producto'].queryset = Producto.objects.filter(empresa=tenant)  # Ajusta esto según tu modelo Producto


class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['producto', 'sucursal', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        tenant = kwargs.get('tenant', None)  # Pasar el tenant desde la vista o usar `request.tenant`
        if tenant:
            # Filtrar sucursales por el tenant actual
            self.fields['sucursal'].queryset = Sucursal.objects.filter(empresa=tenant)
            
            # Filtrar productos, si es necesario
            self.fields['producto'].queryset = Producto.objects.filter(empresa=tenant)