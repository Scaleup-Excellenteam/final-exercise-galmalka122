import asyncio
import os
import sys

import openai

from . import messages
from .logger import logger

openai.api_key = os.getenv("OPENAI_API_KEY")


async def interact(prompt: str):
    """Interacts with the AI and returns the response

    Args:
        prompt (str): prompt to be sent to the AI

    Returns:
        str: response from the AI
    """

    max_retries = 3
    # Set the timeout value (in seconds)
    timeout = 30
    ai_response = {}
    messages.append({"role": "user", "content": prompt})
    for attempt in range(1, max_retries + 1):
        try:
            # Add the message to the conversation and send it to the AI
            print(f"before sending")
            conversation = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                request_timeout=timeout
            )
            ai_response = conversation["choices"][-1]
            if ai_response['finish_reason'] == "stop":
                messages.append(
                    {"role": "assistant", "content": ai_response["message"]["content"]})
                break

        except Exception as e:
            if attempt < max_retries:
                logger.info(
                    f"Request failed: {e}\n trying again (attempt {attempt+1} of {max_retries}).")
                await asyncio.sleep(attempt * 2)
            else:
                logger.error("Maximum number of retries reached. Abort.")
                raise RuntimeError("Maximum number of retries reached. Abort.")
    return ai_response["message"]["content"]

if __name__ == '__main__':
    # Check if a command-line argument is provided
    if len(sys.argv) != 2:
        print("Usage: python openai_interactor.py <path to pptx file>")
        sys.exit(1)

    # Get the presentation file from the command-line argument
    presentation = sys.argv[1]

    # Call the main function with the presentation object
    interact(presentation)
