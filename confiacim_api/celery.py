from celery import Celery

from confiacim_api.conf import settings

celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
    broker_connection_retry_on_startup=True,  # TODO: Pesquisar essa configuração.
)

celery_app.autodiscover_tasks(packages=["confiacim_api"])
