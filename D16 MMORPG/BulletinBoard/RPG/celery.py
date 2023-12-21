import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RPG.settings')

app = Celery('RPG')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'board.tasks.send_mail_monday_8am',
        'schedule': crontab(hour='8', minute='0', day_of_week='1')
    },
}

app.autodiscover_tasks()
