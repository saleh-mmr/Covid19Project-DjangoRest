# Generated by Django 3.1.3 on 2021-01-12 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20201128_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connections',
            name='email',
            field=models.EmailField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='connections',
            name='phone_number',
            field=models.CharField(max_length=15, null=True),
        ),
    ]