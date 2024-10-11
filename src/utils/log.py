import logging
import os
from datetime import datetime

# Create a logs in success and faild for all api's
def setup_logger(log_file):
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    # stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    file_handler.setFormatter(formatter)
    # stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    # logger.addHandler(stream_handler)

    return logger

logger_set = setup_logger(f"colabi.log")