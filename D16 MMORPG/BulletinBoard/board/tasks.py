from celery import shared_task
from django.contrib.auth.models import User
from .models import Poster, Response
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone


@shared_task
def respond_send_email(respond_id):
    respond = Response.objects.get(id=respond_id)
    send_mail(
        subject=f'BulletinBoard: новый отклик на объявление!',
        message=f'Доброго дня, {respond.poster.author}, ! На ваше объявление есть новый отклик!\n'
                f'Прочитать отклик:\nhttp://127.0.0.1:8000/responses/{respond.poster.id}',
        from_email='TixanYgor@yandex.ru',
        recipient_list=[respond.poster.author.email, ],
    )


@shared_task
def respond_accept_send_email(response_id):
    respond = Response.objects.get(id=response_id)
    print(respond.poster.author.email)
    send_mail(
        subject=f'BulletinBoard: Ваш отклик принят!',
        message=f'Доброго дня, {respond.author}, Автор объявления {respond.poster.title} принял Ваш отклик!\n'
                f'Посмотреть принятые отклики:\nhttp://127.0.0.1:8000/responses',
        from_email='TixanYgor@yandex.ru',
        recipient_list=[respond.poster.author.email, ],
    )


@shared_task
def send_mail_monday_8am():
    now = timezone.now()
    list_week_posters = list(Poster.objects.filter(dateCreation__gte=now - timedelta(days=7)))
    if list_week_posters:
        for user in User.objects.filter():
            print(user)
            list_posters = ''
            for poster in list_week_posters:
                list_posters += f'\n{poster.title}\nhttp://127.0.0.1:8000/post/{poster.id}'
            send_mail(
                subject=f'BulletinBoard: посты за прошедшую неделю.',
                message=f'Доброго дня, {user.username}!\nПредлагаем Вам ознакомиться с новыми объявлениями, '
                        f'появившимися за последние 7 дней:\n{list_posters}',
                from_email='TixanYgor@yandex.ru',
                recipient_list=[user.email, ],
            )
