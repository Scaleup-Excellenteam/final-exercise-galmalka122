import argparse
import asyncio
import json
import os

from pptx_explainer import logger, initial_prompt
from pptx_explainer.openai_interactor import interact
from pptx_explainer.presentation_parser import open_presentation, parse_slide


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
    messages = [{"role": "system", "content": initial_prompt}]
    # Open the presentation
    presentation = open_presentation(path)
    responses = {}
    # parse each slide to prompt, and send it to the AI asynchronously
    for index, slide in enumerate(presentation.slides, start=1):
        try:
            prompt = create_slide_prompt(index, slide)
            if prompt is None:
                responses[f"Slide {index}"] = "No text to clarify"
            else:
                res = await interact(prompt, messages)
                responses[f"Slide {index}"] = res
        except ConnectionError as connection_error:
            logger.error(connection_error)
            responses[f"Slide {index}"] = f"Couldn't clarify slide {index}"

    return responses


async def clarify(path):
    """Generates an explanations for a PowerPoint presentation, and saves it to a json file.

    Args:
        path (str): path to the presentation file

    Returns:
        str: path to the json file with the explanations

    Raises:
        PathError: if the path does not exist
        ValueError: if the path is not a pptx file
        Exception: if an error occurs while parsing the presentation
    """
    print(f'Clarifying {os.path.basename(path)}...')
    logger.info(f'Clarifying {os.path.basename(path)}')
    explanations = await process_presentation(path)
    path_dir = os.path.dirname(__file__)
    file_pptx = os.path.basename(path)
    file_json = os.path.join(path_dir, f"{os.path.splitext(file_pptx)[0]}.json")
    with open(file_json, "w") as file:
        json.dump(explanations, file)
    return file_json


if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Script to clarify pptx files.')

    # Add an argument for the file path
    parser.add_argument('file_path', nargs=1, type=str, help='Path to the pptx file')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the file path from the arguments
    file_path = args.file_path

    # Check if the file path argument is missing
    if not file_path:
        parser.error('Please provide a path to the pptx file.')

    try:
        # Call the function to process the file
        asyncio.run(clarify(file_path))
    except Exception as e:
        print(e)
