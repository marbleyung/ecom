# Generated by Django 4.1.5 on 2023-01-28 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0002_post_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(default=0, max_length=200, unique=True, verbose_name='URL'),
            preserve_default=False,
        ),
    ]
