# Generated by Django 2.0.6 on 2018-07-14 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0004_auto_20180714_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='userwebsocketsession',
            name='locked',
            field=models.BooleanField(default=False),
        ),
    ]
