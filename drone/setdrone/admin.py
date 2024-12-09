from django.contrib import admin

# Register your models here.
from .models import Product,Profile

admin.site.register(Product)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number')
    list_filter = ('role',)