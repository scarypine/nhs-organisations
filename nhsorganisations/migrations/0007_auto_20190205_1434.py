# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-02-05 14:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nhsorganisations', '0006_set_new_region_from_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='region_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organisations', to='nhsorganisations.Region', verbose_name='region'),
        ),
    ]