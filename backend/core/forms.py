from django import forms
from .models import Sucursal, Producto, Categoria
from django.contrib.auth.models import User

class SucursalForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Sucursal
        fields = ['nombre', 'direccion', 'telefono', 'codigo_establecimiento', 'punto_emision', 'es_matriz', 'usuarios']
        widgets = {
            'direccion': forms.Textarea(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_establecimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'punto_emision': forms.TextInput(attrs={'class': 'form-control'}),
            'es_matriz': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa 
        if empresa:  # Asignar empresa a la instancia si se proporciona
            self.instance.empresa = empresa 

    def save(self, commit=True):
        print(f"Antes de super().save(): {self}")  # Imprimir el formulario
        instance = super().save(commit=False)  # Crear la instancia
        print(f"Después de super().save(): {instance}") 
        print(f"Valor de self.empresa antes de asignar: {instance.empresa}") 
        instance.empresa = self.empresa 
        print(f"Valor de instance.empresa después de asignar: {instance.empresa}") 
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ProductoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None) 
        super().__init__(*args, **kwargs)
        if self.empresa:
            self.fields['categoria'].queryset = Categoria.objects.filter(empresa=self.empresa)
            self.fields['sucursales'].queryset = Sucursal.objects.filter(empresa=self.empresa)

    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'unidad_medida', 'categoria',
            'sucursales', 'codigo_producto', 'impuesto', 'image'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'sucursales': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'codigo_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'impuesto': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_codigo_producto(self):
        codigo = self.cleaned_data.get('codigo_producto')
        if Producto.objects.filter(codigo_producto=codigo, empresa=self.empresa).exists():
            raise forms.ValidationError(f"El código '{codigo}' ya está en uso para esta empresa.")
        return codigo
    

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']



class PresentacionMultipleForm(forms.Form):
    nombre_presentacion = forms.CharField(max_length=50)
    cantidad = forms.IntegerField(min_value=1)
    precio = forms.DecimalField(max_digits=10, decimal_places=2)
    sucursales = forms.ModelMultipleChoiceField(queryset=Sucursal.objects.all(), widget=forms.CheckboxSelectMultiple)

    def clean(self):
        cleaned_data = super().clean()
        # Validaciones adicionales si es necesario
        return cleaned_data
