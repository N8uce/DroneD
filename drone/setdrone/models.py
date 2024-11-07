from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Product(models.Model):
    TYPE_CHOICES = [
        ('fruit', 'Фрукты'),
        ('treat', 'Лакомства'),
        # добавьте другие типы по необходимости
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='fruit')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.quantity})"
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    city = models.CharField(max_length=100, default='Москва')
    street = models.CharField(max_length=100,default='Тверская улица')
    house = models.CharField(max_length=10,default='20')
    status = models.CharField(max_length=20, default='Pending')
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user}"


    def __str__(self):
        return f"Order {self.id} by {self.user}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username