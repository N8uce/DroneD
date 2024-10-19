from django.core.checks import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, Order
from .forms import OrderForm
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, LoginForm
from django.contrib.auth import login
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

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Получаем продукт или 404
    if product.stock <= 0:  # Проверяем, есть ли товар в наличии
        messages.warning(request, "Этот продукт недоступен.")
        return redirect('cart_detail')  # Возвращаем пользователя на страницу корзины
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
    return redirect('cart_detail')

def cart_detail(request):
    cart_items = []
    total_price = 0  # Инициализация общей стоимости
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            total_price += item.product.price * item.quantity  # Считаем общую стоимость
    else:
        # Для незарегистрированных пользователей получаем данные из сессии
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            cart_items.append({'product': product, 'quantity': quantity})
            total_price += product.price * quantity  # Считаем общую стоимость
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})

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

@login_required
def order_from_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        if request.method == 'POST':
            address = request.POST.get('address')  # Получаем адрес из POST данных
            if address:  # Проверка на наличие адреса в данных
                for item in cart_items:
                    Order.objects.create(
                        user=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        address=address
                    )
                cart_items.delete()  # Очистка корзины после оформления заказа
                return redirect('order_confirmation')
            else:
                messages.error(request, "Адрес не был предоставлен.")
    return render(request, 'order_from_cart.html', {'cart_items': cart_items})

def order_confirmation(request):
    latest_order = Order.objects.filter(user=request.user).last()
    return render(request, 'order_confirmation.html', {'order': latest_order})

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

@login_required
def profile(request):
    return render(request, 'profile.html')









