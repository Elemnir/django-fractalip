# Generated by Django 3.2.3 on 2021-11-05 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fractalip', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='last_ping',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]