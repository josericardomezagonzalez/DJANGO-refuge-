# Generated by Django 2.0.6 on 2018-07-10 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refuge', '0002_petcharacterist'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PetCharacterist',
            new_name='PetCharacteristic',
        ),
    ]
