import inspect
import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import __main__

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Get the path of the caller file
path = os.path.dirname(__main__.__file__)

# Set the paths to the uploads and outputs directories
uploads_directory = os.path.join(path, "uploads")
outputs_directory = os.path.join(path, "outputs")
logs_directory = os.path.join(path, "logs")

# Create the directories if they don't exist
os.makedirs(logs_directory, exist_ok=True)
os.makedirs(uploads_directory, exist_ok=True)
os.makedirs(outputs_directory, exist_ok=True)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a TimedRotatingFileHandler
file_handler = TimedRotatingFileHandler(f'{logs_directory}/explainer.log', when='D', interval=1, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a StreamHandler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)