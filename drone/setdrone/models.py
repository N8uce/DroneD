from django.db import models
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError

class ProductType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField() #тока + значения
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_status(self):
        #Получаем или создаем статус для этого товара
        status_obj, created = ProductStatus.objects.get_or_create(product=self)

        if self.stock > 10:
            status_obj.status = "В наличии"
        elif 1 <= self.stock <= 10:
            status_obj.status = "Ограниченное количество"
        else:
            status_obj.status = "Нет в наличии"

        status_obj.save()
    def clean(self):
        if self.price < 0:
            raise ValidationError({'price': 'Цена не может быть отрицательной.'})
    def save(self, *args, **kwargs):
        self.full_clean()
        self.update_status()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class ProductStatus(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='В наличии')

    def __str__(self):
        return f"{self.product.name}: {self.status}"



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, default='Москва')
    street = models.CharField(max_length=100, default='Тверская улица')
    house = models.CharField(max_length=10, default='20')
    status = models.CharField(max_length=20, default='В процессе')
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user} - {self.product} ({self.quantity})"

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('drone_operator', 'Drone Operator'),
        ('warehouse_manager', 'Warehouse Manager'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telegram_user_id = models.CharField(max_length=255, unique=True, blank=True,null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    telegram_key = models.UUIDField(default=uuid.uuid4, unique=True) #поле с ген. ключом
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"






