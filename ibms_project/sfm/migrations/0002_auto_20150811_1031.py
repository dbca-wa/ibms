# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sfm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sfmmetric',
            name='financialYear',
            field=models.ForeignKey(to='sfm.FinancialYear', on_delete=models.PROTECT),
        ),
    ]
