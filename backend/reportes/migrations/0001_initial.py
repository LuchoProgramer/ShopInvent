# Generated by Django 4.2.8 on 2024-12-18 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facturacion', '0003_cliente_factura_pago'),
        ('core', '0006_alter_producto_empresa'),
        ('RegistroTurnos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_ventas', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_facturas', models.IntegerField(default=0)),
                ('total_efectivo', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('otros_metodos_pago', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('fecha', models.DateField()),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.sucursal')),
                ('turno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportes', to='RegistroTurnos.registroturno')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='MovimientoReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_venta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('pago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='facturacion.pago')),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.sucursal')),
                ('turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RegistroTurnos.registroturno')),
            ],
        ),
    ]
