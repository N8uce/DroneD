# Generated by Django 5.1.2 on 2024-11-02 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setdrone", "0007_product_product_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="address",
        ),
        migrations.AddField(
            model_name="order",
            name="city",
            field=models.CharField(default="Москва", max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="house",
            field=models.CharField(default="20", max_length=10),
        ),
        migrations.AddField(
            model_name="order",
            name="street",
            field=models.CharField(default="Тверская улица", max_length=100),
        ),
    ]
