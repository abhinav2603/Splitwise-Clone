# Generated by Django 2.2.7 on 2019-11-06 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_type', models.CharField(max_length=10)),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=50)),
                ('friends', models.ManyToManyField(related_name='_user_friends_+', to='dashboard.User')),
            ],
        ),
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField(default=0)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.User')),
            ],
            options={
                'unique_together': {('group_id', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='TransactionDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lent', models.FloatField()),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Groups')),
                ('trans_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Transaction')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.User')),
            ],
            options={
                'unique_together': {('trans_id', 'user_id')},
            },
        ),
    ]