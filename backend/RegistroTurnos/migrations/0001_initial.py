# Generated by Django 4.2.8 on 2024-12-18 22:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0006_alter_producto_empresa'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroTurno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio_turno', models.DateTimeField()),
                ('fin_turno', models.DateTimeField(blank=True, null=True)),
                ('total_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_efectivo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('otros_metodos_pago', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.sucursal')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
