# Generated by Django 3.2.9 on 2021-12-20 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20211211_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='dollarProfit',
            field=models.FloatField(default=0),
        ),
    ]
