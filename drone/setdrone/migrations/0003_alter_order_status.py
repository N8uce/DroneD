# Generated by Django 5.1.2 on 2024-12-15 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setdrone", "0002_alter_productstatus_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(default="В процессе", max_length=20),
        ),
    ]
