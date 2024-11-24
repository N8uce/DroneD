# Generated by Django 5.1.2 on 2024-11-24 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setdrone", "0003_alter_order_city_alter_order_house_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="city",
            field=models.CharField(default="Москва", max_length=100),
        ),
        migrations.AlterField(
            model_name="order",
            name="house",
            field=models.CharField(default="20", max_length=10),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(default="Pending", max_length=20),
        ),
        migrations.AlterField(
            model_name="order",
            name="street",
            field=models.CharField(default="Тверская улица", max_length=100),
        ),
    ]
