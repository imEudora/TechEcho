# Generated by Django 5.1.1 on 2024-09-25 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogs", "0008_blog_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="article_pictures/"
            ),
        ),
    ]
