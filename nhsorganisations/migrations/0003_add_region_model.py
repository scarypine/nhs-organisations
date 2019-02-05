# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-02-05 11:53
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('nhsorganisations', '0002_organisation_successor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='e.g. "South West"', max_length=100, verbose_name='name')),
                ('code', models.CharField(help_text='e.g. "Y58"', max_length=20, unique=True, verbose_name='ODS code')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='is active')),
                ('predecessors', models.ManyToManyField(blank=True, related_name='_region_predecessors_+', to='nhsorganisations.Region')),
            ],
            options={
                'verbose_name': 'region',
                'verbose_name_plural': 'regions',
                'ordering': ('name',),
            },
        ),
    ]