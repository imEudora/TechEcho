# Generated by Django 5.1.1 on 2024-09-14 03:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0007_teacher_deleted_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='deleted_at',
        ),
    ]
