# setdrone/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите правильный модуль настроек для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drone.settings')

# Инициализация Celery
app = Celery('drone')

# Используем строку настроек для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач
app.autodiscover_tasks()




