import logging

logger = logging.getLogger("App")
logger.setLevel(logging.DEBUG)

# Define logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a console handler and add it to the logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler and add it to the logger
file_handler = logging.FileHandler(f'{__name__}.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
