import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(levelname)s:%(message)s')


class ApiKeyError(Exception):
    def __str__(self):
        logging.info('Incorrect or Invalid API Key! Please Edit Script to Configure...')
        return 'ApiKeyError'


class ApiError(Exception):
    def __str__(self):
        logging.info('API Error,retry after 20 seconds')
        return 'APIError'


class ConnectionError(Exception):
    def __str__(self):
        logging.info('Try again later...')
        return 'ConnectionError'


class BadImageError(Exception):
    def __str__(self):
        logging.info('Bad image or other request error. Skipping in 10 seconds...')
        return 'BadImageError'


class Non200Error(Exception):
    def __init__(self, errorString):
        self.errorString = errorString

    def __str__(self):
        logging.info(self.errorString)
        return 'Non200Error'


class SearchError(Exception):
    pass


class NoneResultError(Exception):
    pass