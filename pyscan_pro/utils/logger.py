import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with both stream (console) and file handlers.
    Logs are crucial for debugging network applications and keeping a record of scans.
    """
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not logger.handlers:
        # File Handler
        file_handler = RotatingFileHandler(f"logs/{log_file}", maxBytes=5*1024*1024, backupCount=2)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Stream Handler (Optional, GUI might capture stdout independently, 
        # but good for CLI)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

main_logger = setup_logger("PyScanPro", "pyscan.log")
