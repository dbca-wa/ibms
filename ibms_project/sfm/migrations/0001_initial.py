# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CostCentre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('costCentre', models.CharField(help_text='Cost Centre', max_length=6, verbose_name='CostCentre')),
                ('name', models.CharField(max_length=128, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FinancialYear',
            fields=[
                ('financialYear', models.CharField(max_length=10, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MeasurementType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unit', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MeasurementValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(null=True, blank=True)),
                ('comment', models.TextField(null=True)),
                ('costCentre', models.ForeignKey(verbose_name='Related Cost Centre', to='sfm.CostCentre', on_delete=models.PROTECT)),
                ('measurementType', models.ForeignKey(verbose_name='Related MeasurementType', blank=True, to='sfm.MeasurementType', null=True, on_delete=models.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Outcomes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('costCentre', models.ForeignKey(to='sfm.CostCentre', on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name_plural': 'outcomes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Quarter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quarter', models.IntegerField()),
                ('description', models.TextField(null=True)),
                ('financialYear', models.ForeignKey(to='sfm.FinancialYear', on_delete=models.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SFMMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('financialYear', models.CharField(max_length=10)),
                ('servicePriorityNo', models.CharField(default='-1', max_length=100)),
                ('metricID', models.TextField(null=True)),
                ('descriptor', models.TextField(null=True)),
                ('example', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'SFM Metric',
                'verbose_name_plural': 'SFM Metric',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sfmmetric',
            unique_together=set([('financialYear', 'metricID')]),
        ),
        migrations.AddField(
            model_name='measurementvalue',
            name='quarter',
            field=models.ForeignKey(verbose_name='Related Quarter', to='sfm.Quarter', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='measurementvalue',
            name='sfmMetric',
            field=models.ForeignKey(verbose_name='Related SFMMetric', to='sfm.SFMMetric', on_delete=models.PROTECT),
            preserve_default=True,
        ),
    ]
