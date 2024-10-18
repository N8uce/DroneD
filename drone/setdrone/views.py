from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, Order
from .forms import OrderForm
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, LoginForm
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout

def index(request):
    return render(request, "index.html")

def shop(request):
    category = request.GET.get('category')  # Получаем категорию из параметров запроса
    if category:
        products = Product.objects.filter(product_type=category)
    else:
        products = Product.objects.all()  # Если категория не выбрана, выводим все товары

    return render(request, 'shop.html', {'products': products})



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')

def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'cart_detail.html', {'cart_items': cart_items})

def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def order_from_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == 'POST':
        address = request.POST['address']
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                address=address
            )
        cart_items.delete()  # Clear the cart after order is placed
        return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'order_from_cart.html', {'cart_items': cart_items, 'form': form})

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

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
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











