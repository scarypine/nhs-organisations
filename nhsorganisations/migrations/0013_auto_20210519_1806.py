# Generated by Django 2.2.23 on 2021-05-19 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhsorganisations', '0012_auto_20190916_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='organisation_type',
            field=models.CharField(choices=[('provider', 'Provider'), ('commissioner', 'Commissioner'), ('alb', "Arm's Length Body (ALB)"), ('independent-provider', 'Independent Provider'), ('community-provider', 'Community Provider'), ('local-authority', 'Local Authority'), ('pathology-jv', 'Pathology Joint Venture'), ('gp-practice', 'GP Practice'), ('dentist', 'Dentist'), ('pharmacy', 'Pharmacy'), ('other', 'Other')], db_index=True, default='other', max_length=25, verbose_name='organisation type'),
        ),
    ]