# Generated by Django 3.1.5 on 2021-02-22 23:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LFGCore', '0004_auto_20210222_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='LFGCore.address'),
        ),
    ]
