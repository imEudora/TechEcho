# Generated by Django 5.1 on 2024-08-29 08:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0005_question_tags"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="expectations",
        ),
    ]
