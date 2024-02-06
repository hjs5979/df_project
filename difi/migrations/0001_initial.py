# Generated by Django 5.0.1 on 2024-01-19 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='stock',
            fields=[
                ('stock_ticker', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('stock_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='user',
            fields=[
                ('user_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=20)),
                ('user_password', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='stock_value',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('start_date_close', models.IntegerField(null=True)),
                ('end_date_close', models.IntegerField(null=True)),
                ('quantity', models.IntegerField(null=True)),
                ('start_date_close_total', models.IntegerField(null=True)),
                ('end_date_close_total', models.IntegerField(null=True)),
                ('profit_loss', models.IntegerField(null=True)),
                ('return_rate', models.DecimalField(decimal_places=4, max_digits=19, null=True)),
                ('weight', models.DecimalField(decimal_places=4, max_digits=19, null=True)),
                ('stock_ticker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='difi.stock')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='difi.user')),
            ],
            options={
                'unique_together': {('stock_ticker', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='stock_timestamp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('close', models.IntegerField()),
                ('change', models.DecimalField(decimal_places=6, max_digits=19)),
                ('stock_ticker', models.CharField(max_length=6)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='difi.user')),
            ],
            options={
                'unique_together': {('stock_ticker', 'user_id', 'date')},
            },
        ),
    ]
