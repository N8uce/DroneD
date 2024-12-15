# tasks.py
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import telegram
import asyncio
from .models import Profile
from celery import shared_task
from .models import Order
from datetime import timedelta

@shared_task
def send_order_arrival_notification(order_id):
    import logging
    logger = logging.getLogger(__name__)
    try:
        # заказ по ID
        order = Order.objects.get(id=order_id)
        logger.info(f"Обработка заказа {order.id}")

        # Проверка, прошла ли минута с момента оформления (нужно ли?)
        time_diff = timezone.now() - order.ordered_at
        if time_diff >= timedelta(minutes=1):
            # отправка email уведомления
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



# Асинхронная функция для отправки сообщения
async def send_telegram_message(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)

@shared_task
def send_order_telegram_notification(order_id):
    # заказ
    order = Order.objects.get(id=order_id)
    # профиль пользователя, связанный с заказом
    profile = Profile.objects.get(user=order.user)
    # токен
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

    message = (
        f"Заказ №{order.id}\n"
        f"Адрес доставки: {order.city}, {order.street}, {order.house}\n"
        f"Статус: {order.status}"
    )

    try:
        # asyncio.run для асинхронной функции в синхронной задаче
        asyncio.run(send_telegram_message(bot, profile.telegram_user_id, message))
        print(f"Сообщение успешно отправлено пользователю {profile.telegram_user_id}.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


@shared_task
def update_order_status(order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.status == 'В процессе':
            order.status = 'Завершён'  # И змените статус по истечению времени
            order.save()
            return f"Заказ {order_id} обновлён до статуса завершён."
    except Order.DoesNotExist:
        return f"Заказ {order_id} не найден."


