# Generated by Django 3.2.4 on 2021-08-23 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfm', '0006_sfmmetric_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='costcentre',
            name='region',
            field=models.CharField(blank=True, choices=[('Goldfields', 'Goldfields'), ('Kimberley', 'Kimberley'), ('Midwest', 'Midwest'), ('Pilbara', 'Pilbara'), ('South Coast', 'South Coast'), ('South West', 'South West'), ('Swan', 'Swan'), ('Warren', 'Warren'), ('Wheatbelt', 'Wheatbelt')], max_length=100, null=True),
        ),
    ]
