# Generated by Django 3.1.3 on 2020-11-17 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='illness',
            name='illness_name',
        ),
        migrations.RemoveField(
            model_name='status',
            name='status_name',
        ),
    ]