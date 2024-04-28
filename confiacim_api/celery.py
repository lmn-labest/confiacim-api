from celery import Celery

from confiacim_api.conf import settings
from confiacim_api.connection_string import sentinel_connection_url

connection_url = sentinel_connection_url(
    password=settings.SENTINEL_PASSWORD,
    host=settings.SENTINEL_HOST,
    port=settings.SENTINEL_PORT,
)

celery_app = Celery(
    __name__,
    broker=connection_url,
    backend=connection_url,
    broker_connection_retry_on_startup=True,  # TODO: Pesquisar essa configuração.
)

if settings.SENTINEL_MASTER_NAME:
    config_transport = {"master_name": settings.SENTINEL_MASTER_NAME}
    celery_app.conf.broker_transport_options = config_transport
    celery_app.conf.result_backend_transport_options = config_transport

celery_app.autodiscover_tasks(packages=["confiacim_api"])
