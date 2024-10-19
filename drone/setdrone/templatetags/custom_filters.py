from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return value * arg
    except (TypeError, ValueError):
        return ''  # Возвращает пустую строку в случае ошибки
