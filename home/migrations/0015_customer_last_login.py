# Generated by Django 3.2.7 on 2024-11-14 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_auto_20241114_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
