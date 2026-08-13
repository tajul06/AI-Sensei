import logging
def setup_logger(name="trial"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s")
    ch.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(ch)
    return logger

logger = setup_logger()

logger.info("Logger initialized successfully.")
logger.debug("This is a debug message.")
logger.error