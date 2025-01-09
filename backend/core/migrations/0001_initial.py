# Generated by Django 4.2.8 on 2024-12-11 11:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empresas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=20)),
                ('codigo_establecimiento', models.CharField(blank=True, max_length=3, null=True)),
                ('punto_emision', models.CharField(blank=True, max_length=3, null=True)),
                ('es_matriz', models.BooleanField(default=False)),
                ('secuencial_actual', models.CharField(default='000000000', max_length=9)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sucursales', to='empresas.empresa')),
                ('usuarios', models.ManyToManyField(related_name='sucursales', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('codigo_establecimiento', 'punto_emision')},
            },
        ),
    ]