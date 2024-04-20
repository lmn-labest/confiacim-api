from celery import Celery

from confiacim_api.conf import settings

celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True,  # TODO: Pesquisar essa configuração.
)

if settings.SENTINEL_MASTER_NAME:
    config_transport = {"master_name": settings.SENTINEL_MASTER_NAME}
    celery_app.conf.broker_transport_options = config_transport
    celery_app.conf.result_backend_transport_options = config_transport

celery_app.autodiscover_tasks(packages=["confiacim_api"])
