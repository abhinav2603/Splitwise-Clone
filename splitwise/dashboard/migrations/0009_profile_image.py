# Generated by Django 2.2.6 on 2019-11-21 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.FileField(blank=True, upload_to='post_image'),
        ),
    ]
