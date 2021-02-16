# Generated by Django 3.1.5 on 2021-02-16 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LFGCore', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='role',
        ),
        migrations.AddField(
            model_name='member',
            name='roles',
            field=models.ManyToManyField(to='LFGCore.Role'),
        ),
        migrations.AlterField(
            model_name='address',
            name='address2',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='apartment_number',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='endDate',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='telephone_number',
            field=models.DecimalField(decimal_places=0, max_digits=11, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='endDate',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='startDate',
            field=models.DateField(null=True),
        ),
    ]
