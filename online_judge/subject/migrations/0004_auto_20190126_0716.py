# Generated by Django 2.1.4 on 2019-01-26 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subject', '0003_auto_20190121_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(max_length=35),
        ),
    ]