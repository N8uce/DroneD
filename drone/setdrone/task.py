# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import Order, OrderItem

@shared_task
def send_order_arrival_notification(order_id):
    import logging

    logger = logging.getLogger(__name__)  # Логирование

    try:
        # Получаем заказ по ID
        order = Order.objects.get(id=order_id)
        logger.info(f"Обработка заказа {order.id}")

        # Проверяем, прошла ли минута с момента оформления
        time_diff = timezone.now() - order.ordered_at
        if time_diff >= timedelta(minutes=1):
            # Отправляем email уведомление
            subject = "Ваш заказ прибыл!"
            message = f"Ваш заказ №{order.id} прибыл по адресу: {order.city}, {order.street}, {order.house}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [order.user.email]

            send_mail(subject, message, from_email, recipient_list)
            logger.info(f'Email отправлен на {order.user.email}')
        else:
            logger.info(f"Заказ {order.id} еще не готов для отправки уведомления.")
    except Order.DoesNotExist:
        logger.error(f"Заказ с ID {order_id} не найден.")
    except Exception as e:
        logger.error(f'Ошибка при обработке заказа {order_id}: {e}')
