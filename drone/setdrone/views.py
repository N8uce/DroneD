from django.core.checks import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, Order
from django.contrib.auth import authenticate
from .forms import LoginForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages  # Импортируем правильный модуль для сообщений
def index(request):
    return render(request, "index.html")

def shop(request):
    category = request.GET.get('category')  # Получаем категорию из параметров запроса
    if category:
        products = Product.objects.filter(product_type=category)
    else:
        products = Product.objects.all()  # Если категория не выбрана, выводим все товары
    return render(request, 'shop.html', {'products': products})




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Cart


def update_cart_item(request, product_id, action):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_item = Cart.objects.get(product=product, user=request.user)

        if action == 'plus':
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({
                    'success': True,
                    'new_quantity': cart_item.quantity,
                    'new_item_total': cart_item.quantity * float(product.price),
                    'updated_stock': product.stock  # Отправляем актуальный stock
                })
            else:
                return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе.'}, status=400)

        elif action == 'minus':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({
                    'success': True,
                    'new_quantity': cart_item.quantity,
                    'new_item_total': cart_item.quantity * float(product.price),
                    'updated_stock': product.stock  # Отправляем актуальный stock
                })
            else:
                return JsonResponse({'success': False, 'error': 'Минимальное количество товара.'}, status=400)

    return JsonResponse({'success': False, 'error': 'Неверный запрос.'}, status=400)



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Получаем продукт или 404
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Добавление в корзину для авторизованного пользователя
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        else:
            # Добавление в корзину для неавторизованного пользователя (сессия)
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)] += 1  # Увеличиваем количество
            else:
                cart[str(product_id)] = 1  # Добавляем новый товар
            request.session['cart'] = cart  # Сохраняем корзину в сессию

        # Если это обычный POST запрос, перенаправляем обратно на страницу продукта
        return redirect('product_detail', product_id=product.id)

    return redirect('cart_detail')

def cart_detail(request):
    cart_items = []
    total_price = 0  # Initialize total price
    insufficient_stock = False  # Flag to check stock availability
    out_of_stock_items = False  # Flag for items with stock == 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_details = []
        for item in cart_items:
            total_price += item.product.price * item.quantity  # Calculate total price
            if item.product.stock == 0:
                out_of_stock_items = True  # Mark as out of stock
            elif item.quantity > item.product.stock:
                insufficient_stock = True  # Mark as insufficient stock
            cart_details.append({
                'product': item.product,
                'quantity': item.quantity,
                'stock': item.product.stock
            })
    else:
        cart = request.session.get('cart', {})
        cart_details = []
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            if product.stock == 0:
                out_of_stock_items = True  # Mark as out of stock
            elif quantity > product.stock:
                insufficient_stock = True  # Mark as insufficient stock
            cart_details.append({
                'product': product,
                'quantity': quantity,
                'stock': product.stock
            })
            total_price += product.price * quantity  # Calculate total price

    return render(request, 'cart_detail.html', {
        'cart_items': cart_details,
        'total_price': total_price,
        'insufficient_stock': insufficient_stock,  # Pass insufficient stock flag
        'out_of_stock_items': out_of_stock_items  # Pass out-of-stock flag
    })
def remove_from_cart_session(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]  # Удаляем товар из сессии
    request.session['cart'] = cart  # Сохраняем обновленную корзину
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})



import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


from .task import send_order_arrival_notification


from .models import OrderItem
def order_from_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        if request.method == 'POST':
            city = request.POST.get('city')
            street = request.POST.get('street')
            house = request.POST.get('house')
            token = request.POST.get('stripeToken')

            if city and street and house and token:
                try:
                    # Платежная обработка
                    charge = stripe.Charge.create(
                        amount=int(total_price * 100),  # Amount in cents
                        currency='usd',
                        description='Order charge',
                        source=token,
                    )

                    # Создание основного заказа
                    order = Order.objects.create(
                        user=request.user,
                        city=city,
                        street=street,
                        house=house,
                        status="Processing"
                    )

                    # Создание товаров для заказа (OrderItem)
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,  # Привязываем товар к заказу
                            product=item.product,
                            quantity=item.quantity
                        )

                    # Запуск Celery задачи для отправки уведомления через 1 минуту
                    send_order_arrival_notification.apply_async(args=[order.id], countdown=60)

                    cart_items.delete()  # Очистить корзину после заказа
                    messages.success(request, 'Спасибо за ваш заказ!')
                    return redirect('order_confirmation', order_id=order.id)  # Перенаправление на страницу подтверждения заказа

                except stripe.error.StripeError as e:
                    messages.error(request, f'Ошибка при обработке платежа: {e}')
                    return redirect('order_from_cart')  # Перенаправление на ту же страницу в случае ошибки
            else:
                messages.error(request, "Адрес или платежные данные не указаны.")
                return redirect('order_from_cart')  # Перенаправление на ту же страницу, если не указаны все данные

        # Если метод не POST, отображаем страницу с корзиной
        return render(request, 'order_from_cart.html', {'cart_items': cart_items, 'total_price': total_price})

    else:
        # Если пользователь не аутентифицирован, перенаправляем на страницу входа
        return redirect('login')



# views.py
from django.shortcuts import get_object_or_404


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})


import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, Order

from django.shortcuts import render
from .models import Order


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Обновить данные пользователя
            user.email = form.cleaned_data.get('email')
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

from django.contrib.auth import login

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                # Перенос корзины из сессии в корзину авторизованного пользователя
                if 'cart' in request.session:
                    cart_session = request.session['cart']
                    for product_id, quantity in cart_session.items():
                        product = Product.objects.get(id=product_id)
                        cart_item, created = Cart.objects.get_or_create(user=user, product=product)
                        if created:
                            cart_item.quantity = quantity
                        else:
                            cart_item.quantity += quantity
                        cart_item.save()
                    # Очищаем корзину в сессии после переноса
                    del request.session['cart']
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

from django.utils.timezone import now
from datetime import timedelta
@login_required
def profile(request):
    return render(request, 'profile.html')













