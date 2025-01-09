# Generated by Django 4.2.8 on 2024-12-12 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
        ('core', '0005_alter_categoria_empresa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='empresa',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='empresas.empresa'),
        ),
    ]
