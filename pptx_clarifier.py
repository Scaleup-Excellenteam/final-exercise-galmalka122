import asyncio
import json
import os
import sys

from src.logger import logger
from src.openai_interactor import interact
from src.presentation_parser import open_presentation, parse_slide


def create_slide_prompt(index, slide):
    """prepares a slide prompt for the AI

    Args:
        index (int): index of the slide
        slide (slide): slide to be parsed

    Returns:
        str: the prompt for the AI  
    """

    # Prepare the message input for the current slide
    parsed_slide = parse_slide(slide)
    slide_prompt = json.dumps({f"Slide-{index}": parsed_slide})

    # return the message to the AI
    return slide_prompt


async def process_presentation(path: str):
    """Opens a presentation and parses its slides to openai chat prompts.
        Each prompt is sent to the AI asynchronously.

    Args:
        path (str): Path to the presentation file

    Returns:
        list: List of all responses from the AI
    """

    # Open the presentation
    presentation = await open_presentation(path)
    responses = []
    # parse each slide to prompt, and send it to the AI asynchronously
    for index, slide in enumerate(presentation.slides, start=1):
        try:
            prompt = create_slide_prompt(index, slide)
            res = await interact(prompt)
            responses.append(res)
        except Exception as e:
            error_message = f"Error in process_presentation: {e} occurred"
            logger.error(error_message)
            responses.append(error_message)
    return responses


async def clarify(path):
    """Generates an explanations for a PowerPoint presentation, and saves it to a json file.

    Args:
        path (str): path to the presentation file

    Returns:
        list: list of responses from the AI

    Raises:
        PathError: if the path does not exist
        ValueError: if the path is not a pptx file
        Exception: if an error occurs while parsing the presentation
    """

    explanations = await process_presentation(path)
    file_name = os.path.basename(path)
    with open(f"data/{os.path.splitext(file_name)[0]}.json", "w") as file:
        json.dump(explanations, file)


if __name__ == "__main__":

    # Check if the user provided a path to the presentation file
    if len(sys.argv) == 2:
        try:
            # Run the clarification process
            presentation_path = sys.argv[1]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(clarify(presentation_path))
        except Exception as e:
            print(e)
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(clarify('data/test.pptx'))
        print("Please provide a path to pptx file.")
