import logging


def setupLogging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)