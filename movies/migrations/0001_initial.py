# Generated by Django 3.1.7 on 2021-04-27 06:46

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('availability', models.BooleanField(auto_created=True)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(max_length=1000)),
                ('stock', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('rental_price', models.FloatField()),
                ('sale_price', models.FloatField()),
                ('likes', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Sell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('total', models.FloatField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['total'],
            },
        ),
        migrations.CreateModel(
            name='Rent',
            fields=[
                ('sell_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='movies.sell')),
                ('return_date', models.DateTimeField(default=datetime.datetime(2021, 5, 2, 6, 46, 30, 387286, tzinfo=utc))),
                ('returned', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-return_date'],
            },
            bases=('movies.sell',),
        ),
        migrations.CreateModel(
            name='MovieImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(upload_to='')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='movies.movie')),
            ],
        ),
        migrations.CreateModel(
            name='MovieChangesLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_title', models.CharField(max_length=100)),
                ('old_rental_price', models.FloatField()),
                ('old_sale_price', models.FloatField()),
                ('new_title', models.CharField(max_length=100)),
                ('new_rental_price', models.FloatField()),
                ('new_sale_price', models.FloatField()),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
            ],
            options={
                'ordering': ['updated_at'],
            },
        ),
        migrations.CreateModel(
            name='LikeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]