import configparser
import colorlog
import logging


def init_logger():
    global logger
    if logger is None:
        logger = colorlog.getLogger('app')
        log_level = logging.INFO
        try:
            if config['LOG']["log_level"] == "debug": log_level = logging.DEBUG
            if config['LOG']["log_level"] == "info": log_level = logging.INFO
            if config['LOG']["log_level"] == "warning": log_level = logging.WARNING
            if config['LOG']["log_level"] == "error": log_level = logging.ERROR
        except:
            pass
        logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s %(levelname)s: %(message)s (%(module)s:%(lineno)d)')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

logger = None
init_logger()

def init_config():
    global config,server
    config_file = "../config/app.conf"
    config = configparser.ConfigParser()
    config.read(config_file)
    server = config['SERVER']

config,server = None, None
init_config()