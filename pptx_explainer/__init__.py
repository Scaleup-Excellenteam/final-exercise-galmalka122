import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler


from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

initial_prompt = """
You supply concise and to the point explanations about PowerPoint slides.


###


Instructions: 1. Please wait for the first slide before generating explanations. The slide data will be provided 
individually. 2. Once you receive each slide, analyze its contents and generate a captivating explanation based on 
the slide's title and text. 3. Provide a medium level of detail in your explanations, striking a balance between 
summaries and detailed explanations. 4. Consider the context of previous slides when generating responses to maintain 
a coherent and cohesive explanation throughout the presentation. 5. Ensure that your responses flow smoothly from one 
slide to the next, maintaining a logical progression of ideas. 6. If no explanation can be provided, respond with the 
original title and make suggestions about what could be covered on the slide. 7. Provide only the explanation text 
without any additional interaction.


Data Format: The presentation data should be provided as a list of slide objects. Each slide object should be sent in 
a separate request and follow this format: { "slide-{slide number}": { "title": "Title of the slide", "text": ["Text 
content of the slide"] } }


Response Format:
The response should include only the explanation text for each slide.


As we automate this process, please respond with the word 'send' to indicate that you are ready to receive the first 
slide. Let's proceed with the automated analysis of the slides, ensuring that we receive concise and straightforward 
explanations for each slide without any interactive text.


"""

load_dotenv()

path = os.path.dirname(__file__)

# Set the paths to the uploads and outputs directories
uploads_directory = os.path.join(path, "uploads")
outputs_directory = os.path.join(path, "outputs")
logs_directory = os.path.join(path, "logs")

os.makedirs(logs_directory, exist_ok=True)
os.makedirs(uploads_directory, exist_ok=True)
os.makedirs(outputs_directory, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Define logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a TimedRotatingFileHandler and add it to the logger
file_handler = TimedRotatingFileHandler(f'{logs_directory}/explainer.log', when='D', interval=1, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

