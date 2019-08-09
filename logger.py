import logging
from settings import project_directory
from helpers import create_directory


class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level


# def setup_logger(site_name):
#     logging.getLogger('').setLevel(logging.DEBUG)
#     logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
#
#     my_logger = logging.getLogger('my_logger')
#
#     formatter = logging.Formatter('%(funcName)s - %(levelname)s - %(message)s')
#     info_handler = logging.FileHandler(filename=project_directory + site_name + '/parse.log', mode='w')
#     info_handler.setLevel(logging.INFO)
#     warning_handler = logging.FileHandler(filename=project_directory + site_name + '/warning.log', mode='w')
#     warning_handler.setLevel(logging.WARNING)
#     errors_handler = logging.FileHandler(filename=project_directory + site_name + '/error.log', mode='w')
#     errors_handler.setLevel(logging.ERROR)
#
#     info_handler.setFormatter(formatter)
#     warning_handler.setFormatter(formatter)
#     errors_handler.setFormatter(formatter)
#
#     my_logger.addHandler(info_handler)
#     my_logger.addHandler(warning_handler)
#     my_logger.addHandler(errors_handler)
#
#     info_handler.addFilter(MyFilter(logging.INFO))
#     warning_handler.addFilter(MyFilter(logging.WARNING))
#     errors_handler.addFilter(MyFilter(logging.ERROR))
#     return my_logger

logging.getLogger('').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

my_logger = logging.getLogger('my_logger')


def setup_logger(site_name):
    formatter = logging.Formatter('%(funcName)s - %(levelname)s - %(message)s')
    info_handler = logging.FileHandler(filename=project_directory + site_name + '/parse.log', mode='w')
    info_handler.setLevel(logging.INFO)
    warning_handler = logging.FileHandler(filename=project_directory + site_name + '/warning.log', mode='w')
    warning_handler.setLevel(logging.WARNING)
    errors_handler = logging.FileHandler(filename=project_directory + site_name + '/error.log', mode='w')
    errors_handler.setLevel(logging.ERROR)

    info_handler.setFormatter(formatter)
    warning_handler.setFormatter(formatter)
    errors_handler.setFormatter(formatter)

    my_logger.addHandler(info_handler)
    my_logger.addHandler(warning_handler)
    my_logger.addHandler(errors_handler)

    info_handler.addFilter(MyFilter(logging.INFO))
    warning_handler.addFilter(MyFilter(logging.WARNING))
    errors_handler.addFilter(MyFilter(logging.ERROR))


if __name__ == '__main__':
    create_directory('test')
    setup_logger('test')
    my_logger.info('info')
    my_logger.warning('warning')
    my_logger.error('error')
    my_logger.debug('debug')

