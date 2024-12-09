"""
URL configuration for drone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from setdrone import views
from setdrone.views import ProductStatisticsView
urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('admin/', admin.site.urls),
    path('shop/', views.shop, name='shop'),  # Магазин
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-from-cart/', views.order_from_cart, name='order_from_cart'),
    path('remove-from-cart-session/<int:product_id>/', views.remove_from_cart_session, name='remove_from_cart_session'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('cart_count/', views.cart_count, name='cart_count'),
    path('manager/statistics/', ProductStatisticsView.as_view(), name='manager_statistics'),
    path('drone-operator/', views.drone_operator_dashboard, name='drone_operator_dashboard'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)










