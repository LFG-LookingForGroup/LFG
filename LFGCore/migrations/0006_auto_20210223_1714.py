# Generated by Django 3.1.5 on 2021-02-23 22:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LFGCore', '0005_auto_20210222_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='LFGCore.skill'),
        ),
    ]
