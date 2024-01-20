from colorlog import ColoredFormatter
import colorlog

handler = colorlog.StreamHandler()

formatter = ColoredFormatter(
    "%(log_color)s%(name)-20s  %(funcName)-30s  %(levelname)-10s  %(asctime)s  %(message_log_color)s%(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'black,bg_red',
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'black,bg_red',
        }
    },
    style='%'
)

handler.setFormatter(formatter)


def get_logger(name: str, level='DEBUG'):
    logger = colorlog.getLogger(name.upper())
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
