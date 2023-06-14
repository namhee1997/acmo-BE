from pydantic import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os
from celery.schedules import crontab

load_dotenv()
config = {
    "PORT": os.environ.get("PORT"),
    "DATABASE_URI": f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@localhost/{os.environ.get('POSTGRES_DB')}",
    "SECRET_KEY": os.environ.get("SECRET_KEY"),
    "ALGORITHM": os.environ.get("ALGORITHM"),
    "API_V1_STR" : "/api/v1",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 1440,
    "SENDINBLUE_API_KEY": os.environ.get("SENDINBLUE_API_KEY"),
    "HOSTING_URL": os.environ.get("HOSTING_URL"),
    "EMAIL_RECEIVER": os.environ.get("EMAIL_RECEIVER"),
    "EMAIL_SENDER": os.environ.get("EMAIL_SENDER"),
    "SENTRY_DSN": os.environ.get("SENTRY_DSN"),
    "EMAIL_ENABLED": os.environ.get("EMAIL_ENABLED"),
    "USER_VERIFY_EMAIL_TEMPLATE": os.environ.get("USER_VERIFY_EMAIL_TEMPLATE"),
    "EXPIRES_VERIFY_TOKEN_DELTA": 24,
    "ENVIRONMENT": os.environ.get("ENVIRONMENT"),
    "EXPIRES_RESET_TOKEN_IN_HOURS": os.environ.get("EXPIRES_RESET_TOKEN_IN_HOURS"),
    "USER_RESET_PASSWORD_EMAIL_TEMPLATE": os.environ.get("USER_RESET_PASSWORD_EMAIL_TEMPLATE"),
    "USER_WELCOME_EMAIL_TEMPLATE": os.environ.get("USER_WELCOME_EMAIL_TEMPLATE"),
    "USER_TOP_UP_CONFIRM_EMAIL_TEMPLATE": os.environ.get("USER_TOP_UP_CONFIRM_EMAIL_TEMPLATE"),
    "USER_CONFIRM_EMAIL_URL": os.environ.get("USER_CONFIRM_EMAIL_URL"),
}



class CeleryConfig(BaseSettings):
    result_backend: Optional[str]
    broker_url: Optional[str]

    accept_content = ['pickle', 'json']
    task_serializer = ['pickle']

    C_FORCE_ROOT = True
    # worker_hijack_root_logger = False
    task_always_eager: bool = False

    timezone = 'UTC'

    PYPPETEER_HOME: Optional[str]

    """
    REGISTER DISTRIBUTED TASKS HERE
    Ref: http://bit.ly/2xldMEC
    Gather celery tasks in others modules.
    Remeber audodiscover_task searches a list of packages for a "tasks.py" module.
    You have to list here all the task-module you have:
    """
    register_tasks = [
    ]

    """ 
    `include` is an important config that loads needed modules to the worker
    Don't delete rows, only add the new module here.
    See problem at https://stackoverflow.com/q/55998650/1235074
    """
    include = register_tasks + [
        'app',
        'app.infra.tasks.email',
        'app.infra.tasks.order',
        'app.infra.tasks.smm_service',
        'app.infra.tasks.order_complete',
        'app.infra.tasks.user.email',
        'app.infra.tasks.customer.add_customer',
        'app.infra.tasks.customer.update_customer',
        'app.infra.tasks.abandon.coupon_email',
        'app.infra.tasks.abandon.default_email'
    ]

    """
    celery beat schedule tasks
    """
    beat_schedule = {
        'check_order_status': {
            'task': 'app.infra.tasks.order.check_order_status',
            'schedule': crontab(minute='*/5'),  # for every 1 hour
            'args': None
        },
        'send-alert-email-for-error-orders-every-12-hours': {
            'task': 'app.infra.tasks.email.send_alert_email_for_error_orders',
            'schedule': crontab(minute=0, hour='*/12'),  # for every 12 hours
            'args': None
        },
        'push-orders-to-google-sheet-every-day': {
            'task': 'app.infra.tasks.order.push_orders_to_gsheet',
            'schedule': crontab(minute=58, hour=16),  # for 23:58
            'args': None
        },
        'process-confirmed-order-every-hour': {
            'task': 'app.infra.tasks.order.process_confirmed_order',
            'schedule': crontab(minute=0, hour='*/1'),
            'args': None
        },
        'proccess-send-abandon-email-every-10-minutes': {
            'task': 'app.infra.tasks.abandon.default_email.proccess_send_abandon_email',
            'schedule': crontab(minute='*/10'), # for every 10 minutes
            'args': None
        },
        'proccess-send-coupon-abandon-email-every-10-minutes': {
            'task': 'app.infra.tasks.abandon.coupon_email.process_coupon_customer_abandon_email',
            'schedule': crontab(minute='*/10'), # for every 10 minutes
            'args': None
        },
        'process-private-amount-every-3-minutes': {
            'task': 'app.infra.tasks.smm_service.process_private_amount',
            'schedule': crontab(minute='*/3'), # for every 3 minutes
            'args': None
        },
        'process-send-email-order-complete-after-12-hours-every-15-minutes': {
            'task': 'app.infra.tasks.order_complete.proccess_send_email_complete_after_12_hours',
            'schedule': crontab(minute='*/15'),  # for every 15 minutes
            'args': None
        },
    }

    class Config:
        env_file = '.env'

