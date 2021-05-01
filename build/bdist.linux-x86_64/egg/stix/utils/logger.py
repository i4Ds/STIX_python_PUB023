import logging


class QtHandler(logging.Handler):
    def __init__(self, qt_widget):
        logging.Handler.__init__(self)
        self.widget = qt_widget

    def emit(self, record):
        record = self.format(record)
        self.widget.showMessage(record, 0)
        self.widget.showMessage(record, 1)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s - %(name)s',
                                  datefmt='%Y-%m-%dT%H:%M:%SZ')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger