from django.core.checks import messages
from django.contrib.auth import authenticate
from .forms import LoginForm
from .forms import SignUpForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import Cart
from django.http import JsonResponse
import stripe
from django.conf import settings
from .task import send_order_arrival_notification, send_order_telegram_notification, update_order_status
from .models import Profile
from django.contrib.auth import login
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from .models import OrderItem
from django.contrib.auth.decorators import login_required
from .models import Order
from .models import ProductStatus
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from .models import Product


# представление главной страницы
def index(request):
    return render(request, "index.html")


def get_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        cart = request.session.get('cart', {})
        print("Cart session data:", cart)  # навсякий
        cart_count = sum(item.get('quantity', 0) for item in cart.values())
    return cart_count


def cart_count(request):
    cart_count = get_cart_count(request)
    return JsonResponse({'cart_count': cart_count})


# представление страницы магазина
def shop(request):
    category = request.GET.get('category')
    products = Product.objects.all()
    if category:
        products = products.filter(product_type__name=category)

    # сортировка через order_by прям как в sql
    products = products.order_by('name')
    # Обновляем статус для каждого продукта
    for product in products:
        product.update_status()  # Обновляем статус на основе текущего количества
        product.save()
    # статусы для продуктов
    product_statuses = {status.product.id: status.status for status in
                        ProductStatus.objects.filter(product__in=products)}

    return render(request, 'shop.html', {
        'products': products,
        'product_statuses': product_statuses,
    })


# представление, чтобы динамически изменять
# на странице корзины кол-во товара в корзине
def update_cart_item(request, product_id, action):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        # проверка на всякий
        print("Cart structure:", cart)
        if str(product_id) not in cart:
            return JsonResponse({'success': False, 'error': 'Товар не в корзине.'}, status=400)

        cart_item = cart[str(product_id)]
        print("Cart item structure:", cart_item)

        if isinstance(cart_item, int):
            return JsonResponse({'success': False, 'error': 'С корзинной структурой что-то не так.'}, status=400)

        if action == 'plus':
            if cart_item['quantity'] < product.stock:
                cart_item['quantity'] += 1
                cart_item['item_total'] = cart_item['quantity'] * float(product.price)
            else:
                return JsonResponse({'success': False, 'error': 'Недостаточный запас.'}, status=400)

        elif action == 'minus':
            if cart_item['quantity'] > 1:
                cart_item['quantity'] -= 1
                cart_item['item_total'] = cart_item['quantity'] * float(product.price)
            else:
                return JsonResponse({'success': False, 'error': 'Достигнуто минимальное количество.'}, status=400)

        cart[str(product_id)] = cart_item
        request.session['cart'] = cart
        return JsonResponse({
            'success': True,
            'new_quantity': cart_item['quantity'],
            'new_item_total': cart_item['item_total'],
            'updated_stock': product.stock
        })

    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, product=product, user=request.user)

        if action == 'plus':
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({
                    'success': True,
                    'new_quantity': cart_item.quantity,
                    'new_item_total': cart_item.quantity * float(product.price),
                    'updated_stock': product.stock
                })
            else:
                return JsonResponse({'success': False, 'error': 'Недостаточный запас.'}, status=400)

        elif action == 'minus':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({
                    'success': True,
                    'new_quantity': cart_item.quantity,
                    'new_item_total': cart_item.quantity * float(product.price),
                    'updated_stock': product.stock
                })
            else:
                return JsonResponse({'success': False, 'error': 'Достигнуто минимальное количество.'}, status=400)

    return JsonResponse({'success': False, 'error': 'Неверный запрос.'}, status=400)


# представление чтобы добавлять товары в корзину
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart_item = cart[str(product_id)]
            cart_item['quantity'] += 1
            cart_item['item_total'] = cart_item['quantity'] * float(product.price)
        else:
            cart[str(product_id)] = {
                'quantity': 1,
                'item_total': float(product.price)
            }
        request.session['cart'] = cart
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        cart_count = sum(item['quantity'] for item in request.session.get('cart', {}).values())

    return JsonResponse({'cart_count': cart_count})


# корзина
def cart_detail(request):
    cart_items = []
    total_price = 0
    insufficient_stock = False
    out_of_stock_items = False

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_details = []
        for item in cart_items:
            total_price += item.product.price * item.quantity
            if item.product.stock == 0:
                out_of_stock_items = True
            elif item.quantity > item.product.stock:
                insufficient_stock = True
            cart_details.append({
                'product': item.product,
                'quantity': item.quantity,
                'stock': item.product.stock
            })
    else:
        cart = request.session.get('cart', {})
        cart_details = []
        for product_id, cart_item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            quantity = cart_item['quantity']  # извлечение кол-ва из корзины очевидно...
            if product.stock == 0:
                out_of_stock_items = True
            elif quantity > product.stock:
                insufficient_stock = True
            cart_details.append({
                'product': product,
                'quantity': quantity,
                'stock': product.stock
            })
            total_price += product.price * quantity

    return render(request, 'cart_detail.html', {
        'cart_items': cart_details,
        'total_price': total_price,
        'insufficient_stock': insufficient_stock,
        'out_of_stock_items': out_of_stock_items
    })


def remove_from_cart_session(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]  # del товар из сессии
    request.session['cart'] = cart  # save обновленную корзину
    return redirect('cart_detail')


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        # работаем с корзиной в модели Cart
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        cart_item.delete()
    else:
        # работаем с корзиной в сессии
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
        request.session['cart'] = cart

    return redirect('cart_detail')


# представление для доп информации о товаре
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


# Ключик stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


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
                    # Платежная обработка, наверное
                    charge = stripe.Charge.create(
                        amount=int(total_price * 100),
                        currency='rub',
                        description='Order charge',
                        source=token,
                    )
                    # cоздание заказа
                    order = Order.objects.create(
                        user=request.user,
                        city=city,
                        street=street,
                        house=house,
                        status="В процессе"
                    )

                    # cоздание товаров для заказа (OrderItem) и уменьшение количества на складе
                    for item in cart_items:
                        # проверка доступного кол-во на складе
                        if item.quantity > item.product.stock:
                            messages.error(request, f"Недостаточно товара '{item.product.name}' на складе.")
                            return redirect('cart_detail')

                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity
                        )

                        # -кол-ва товара на складе
                        item.product.stock -= item.quantity
                        item.product.save()

                    # Задачи для celery
                    update_order_status.apply_async((order.id,), countdown=60)  # таймер на минуту
                    send_order_arrival_notification.apply_async(args=[order.id], countdown=60)
                    send_order_telegram_notification.apply_async(args=[order.id], countdown=60)

                    cart_items.delete()  # очистка корзины после заказа
                    messages.success(request, 'Спасибо за ваш заказ!')
                    return redirect('order_confirmation', order_id=order.id)

                except stripe.error.StripeError as e:
                    messages.error(request, f'Ошибка при обработке платежа: {e}')
                    return redirect('order_from_cart')
            else:
                messages.error(request, "Адрес или платежные данные не указаны.")
                return redirect('order_from_cart')

        return render(request, 'order_from_cart.html', {'cart_items': cart_items, 'total_price': total_price})

    else:
        return redirect('login')


# представление страницы подтверждения заказа
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.email = form.cleaned_data.get('email')
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.save()
            login(request, user)  # авторизация
            # перенос корзины из сессии в корзину авторизованного пользователя
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

                # Очисточка -_- корзины в сессии после переноса
                del request.session['cart']

            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                # перенос корзины из сессии в корзину авторизованного пользователя
                if 'cart' in request.session:
                    cart_session = request.session['cart']
                    for product_id, cart_item in cart_session.items():
                        product = Product.objects.get(id=product_id)
                        quantity = cart_item['quantity']  # Extract quantity from dictionary
                        cart_db_item, created = Cart.objects.get_or_create(user=user, product=product)
                        if created:
                            cart_db_item.quantity = quantity
                        else:
                            cart_db_item.quantity += quantity
                        cart_db_item.save()
                    # Очистка корзины из сессии после входа в аккаунт
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
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


class ProductStatisticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'manager_statistics.html'

    def test_func(self):
        return self.request.user.profile.role == 'warehouse_manager'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        context['products'] = products
        context['total_sold'] = {product.id: self.get_total_sold(product) for product in products}
        return context

    def get_total_sold(self, product):
        return OrderItem.objects.filter(product=product).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0


@login_required
def drone_operator_dashboard(request):
    current_orders = Order.objects.prefetch_related('orderitem_set__product').filter(
        status__in=['В процессе', 'Завершён']
    )
    context = {
        'current_orders': current_orders,
    }
    return render(request, 'drone_operator_dashboard.html', context)
