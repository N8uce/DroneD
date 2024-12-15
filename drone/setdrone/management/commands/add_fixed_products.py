from django.core.management.base import BaseCommand
from setdrone.models import Product, ProductType

class Command(BaseCommand):
    help = 'Добавление товаров по бырому'
    def handle(self, *args, **kwargs):
        product_types = {
            'fruit': ProductType.objects.get_or_create(name='Фрукты')[0],
            'treat': ProductType.objects.get_or_create(name='Лакомства')[0],
            'semi': ProductType.objects.get_or_create(name='Полуфабрикаты')[0],
            'vegetables': ProductType.objects.get_or_create(name='Овощи')[0],
            'meat': ProductType.objects.get_or_create(name='Мясо')[0],
            'dairy': ProductType.objects.get_or_create(name='Молочные продукты')[0],
            'bakery': ProductType.objects.get_or_create(name='Выпечка')[0],
            'beverages': ProductType.objects.get_or_create(name='Напитки')[0],
            'seafood': ProductType.objects.get_or_create(name='Морепродукты')[0],
        }

        products = [
            {'name': 'Яблоки', 'description': 'Свежие яблоки с фермы.', 'price': 100.00, 'stock': 50, 'product_type': 'fruit'},
            {'name': 'Бананы', 'description': 'Спелые бананы из Эквадора.', 'price': 120.00, 'stock': 40, 'product_type': 'fruit'},
            {'name': 'Шоколадный батончик', 'description': 'Молочный шоколад с орехами.', 'price': 60.00, 'stock': 100, 'product_type': 'treat'},
            {'name': 'Пицца замороженная', 'description': 'Классическая пицца с сыром и колбасой.', 'price': 300.00, 'stock': 20, 'product_type': 'semi'},
            {'name': 'Картофель', 'description': 'Молодой картофель.', 'price': 30.00, 'stock': 70, 'product_type': 'vegetables'},
            {'name': 'Куриное филе', 'description': 'Филе цыпленка охлажденное.', 'price': 250.00, 'stock': 25, 'product_type': 'meat'},
            {'name': 'Молоко', 'description': 'Свежее пастеризованное молоко.', 'price': 50.00, 'stock': 60, 'product_type': 'dairy'},
            {'name': 'Багет', 'description': 'Французский багет.', 'price': 40.00, 'stock': 30, 'product_type': 'bakery'},
            {'name': 'Минеральная вода', 'description': 'Газированная минеральная вода.', 'price': 20.00, 'stock': 80, 'product_type': 'beverages'},
            {'name': 'Креветки', 'description': 'Креветки очищенные, замороженные.', 'price': 400.00, 'stock': 15, 'product_type': 'seafood'},
        ]

        for product in products:
            Product.objects.create(
                name=product['name'],
                description=product['description'],
                price=product['price'],
                stock=product['stock'],
                product_type=product_types[product['product_type']]
            )

        self.stdout.write(self.style.SUCCESS('Successfully added fixed products.'))
