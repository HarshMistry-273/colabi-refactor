from datetime import time
from src.utils.utils import PineConeConfig
from src.celery_worker import celery_app


@celery_app.task()
def embedded_docs(api_key, index_name, namespace, file_path, file_type):
    pc = PineConeConfig(
        api_key=api_key,
        index_name=index_name,
        namespace=namespace,
        file_path=file_path,
        file_type=file_type,
    )

    return "Docs embedded successfully"
