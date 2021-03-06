# Generated by Django 3.2.9 on 2021-11-02 12:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=20)),
                ('treasure', models.FloatField(default=100000)),
                ('treasureUSD', models.FloatField(default=0)),
                ('globalMarketPrice', models.FloatField(default=0)),
                ('lockedBTCtot', models.FloatField(default=0)),
                ('vol24H', models.FloatField(default=0)),
                ('volTot', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orders', models.JSONField(default=dict)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='price',
        ),
        migrations.RemoveField(
            model_name='order',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.AddField(
            model_name='order',
            name='USDprice',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='history',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='order',
            name='placer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='placer', to='app.profile'),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Open'), (2, 'Closed'), (3, 'Failed'), (4, 'Canceld')], default=1),
        ),
        migrations.AddField(
            model_name='order',
            name='type',
            field=models.IntegerField(choices=[(1, 'Buy_Market'), (2, 'Sell_market'), (3, 'Buy_Limit_fast'), (4, 'Sell_limit_fast'), (5, 'Buy_Limit_full'), (6, 'Sell_limit_full'), (99, 'Referral')], default=1),
        ),
        migrations.AddField(
            model_name='profile',
            name='btc',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='lockedBTC',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='lockedUSD',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='ownReferral',
            field=models.CharField(default='-----', max_length=5),
        ),
        migrations.AddField(
            model_name='profile',
            name='usd',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='usedReferral',
            field=models.CharField(default='-----', max_length=5),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'exchange'), (99, 'referral')], default=1)),
                ('amount', models.FloatField(default=0)),
                ('USDprice', models.FloatField(default=0)),
                ('totalUSDvalue', models.FloatField(default=0)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order', to='app.order')),
                ('receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver', to='app.profile')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sender', to='app.profile')),
            ],
        ),
    ]
