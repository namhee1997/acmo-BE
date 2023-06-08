"""Celery worker module"""
import logging
from logging.handlers import TimedRotatingFileHandler
from celery import Celery, signals
from celery.signals import after_setup_logger
import sentry_sdk

from app.config import CeleryConfig, config


# sentry_sdk.init(
#     dsn='https://77a8db3290824b31a4ab6733ca1ccee6@o4504325487460352.ingest.sentry.io/4504649166553088',
#     integrations=[
#         CeleryIntegration(),
#     ],

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production,
#     traces_sample_rate=1.0,
# )


celery_config = CeleryConfig()

logger = logging.getLogger(__name__)

celery = Celery('acmo_celery_worker', broker=celery_config.broker_url)
celery.config_from_object(celery_config)

@signals.worker_init.connect
def init_sentry(**_kwargs):
    if config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            traces_sample_rate=1.0,
            debug=False
        )


def celery_delay(task, *args, **kwargs):
    """Helper function for celery task
    
    Arguments:
        task {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    def actually_send(**options):
        return task.s(*args, **kwargs).apply_async(**options)

    return actually_send


@after_setup_logger.connect
def config_loggers(logger, *args, **kwags):
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')

    # StreamHandler
    # sh = logging.StreamHandler()
    # sh.setFormatter(formatter)
    # logger.addHandler(sh)

    handler = TimedRotatingFileHandler(
        '/app/logs/celery_{}.log'.format(config.ENVIRONMENT),
        when='W0',
        utc=True,
        backupCount=5
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

if __name__ == '__main__':
    celery.worker_main()
