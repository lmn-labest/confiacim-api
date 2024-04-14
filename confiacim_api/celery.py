from celery import Celery

from confiacim_api.conf import settings

celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True,  # TODO: Pesquisar essa configuração.
)

celery_app.conf.broker_transport_options = {"master_name": "mymaster"}
celery_app.conf.result_backend_transport_options = {"master_name": "mymaster"}

celery_app.autodiscover_tasks(packages=["confiacim_api"])
