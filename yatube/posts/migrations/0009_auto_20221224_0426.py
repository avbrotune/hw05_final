# Generated by Django 2.2.16 on 2022-12-23 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20221223_2329'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='uniq_follow',
        ),
    ]
