import asyncio
import os
import shutil

import openai.error

from ..definitions import uploads_directory, outputs_directory
from pptx_clarifier.pptx_explainer.pptx_explainer import clarify
from pptx_clarifier.pptx_explainer import explainer_logger as logger


def get_file_name(path):
    if os.path.isfile(path):
        file = os.path.basename(path)
        return os.path.splitext(file)[0]


# Create a console handler and add it to the logger
files_in_process = set()
files = [get_file_name(os.path.join(outputs_directory, path)) for path in os.listdir(outputs_directory)]

processed_files = set(files)


def scan_directories():
    # Scan the uploads directory for files

    upload_files = os.listdir(uploads_directory)
    unprocessed_files = []
    for file in upload_files:
        file = os.path.join(uploads_directory, file)
        if get_file_name(file) not in processed_files and get_file_name(file) not in files_in_process:
            unprocessed_files.append(file)
    logger.info(f"{len(unprocessed_files)} new files added: " +
                ''.join(f'{file_name} ' for file_name in unprocessed_files))
    return unprocessed_files


def error_handler(file_name: str, error: Exception):
    logger.error(f"Error processing {file_name}: {error}")
    os.remove(file_name)
    files_in_process.remove(get_file_name(file_name))


async def clarify_file(file_name: str):
    # Add the file to the files in process set
    files_in_process.add(get_file_name(file_name))
    logger.info(f"Processing {file_name}")
    try:
        json_path = await clarify(file_name)
    except FileNotFoundError as file_not_found_error:
        error_handler(file_name, file_not_found_error)
        return
    except ValueError as value_error:
        error_handler(file_name, value_error)
        return
    except openai.error.OpenAIError as openai_error:
        error_handler(file_name, openai_error)
        return
    # Move the file to the outputs directory to mark it as processed
    shutil.move(json_path, outputs_directory)
    logger.info(f"Moved {file_name} to {outputs_directory}")
    files_in_process.remove(get_file_name(file_name))
    processed_files.add(get_file_name(file_name))


async def explainer():
    while True:
        try:
            # Scan the uploads directory for files
            unprocessed_files = scan_directories()
            for file in unprocessed_files:
                await clarify_file(file)
            await asyncio.sleep(5)
        except Exception as e:
            logger


if __name__ == "__main__":
    asyncio.run(explainer())
