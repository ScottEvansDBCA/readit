# Generated by Django 2.0.6 on 2018-08-01 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_temppost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temppost',
            name='categories',
        ),
        migrations.DeleteModel(
            name='TempPost',
        ),
    ]