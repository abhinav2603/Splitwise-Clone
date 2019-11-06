# Generated by Django 2.2.7 on 2019-11-06 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20191106_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='group_name',
            field=models.CharField(default='Defualt', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='groups',
            name='users',
            field=models.ManyToManyField(to='dashboard.User'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='title',
            field=models.CharField(default='Default', max_length=140),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='groups',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='groups',
            name='user',
        ),
    ]