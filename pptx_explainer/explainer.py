import asyncio
import os
import shutil

from pptx_explainer import uploads_directory, outputs_directory, logger
from pptx_explainer.pptx_clarifier import clarify


def get_file_name(path):
    if os.path.isfile(path):
        file = os.path.basename(path)
        return os.path.splitext(file)[0]


# Create a console handler and add it to the logger
files_in_process = set()
files = [get_file_name(path) for path in os.listdir(outputs_directory)]

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


async def clarify_file(file_name: str):
    # Add the file to the files in process set
    files_in_process.add(get_file_name(file_name))
    logger.info(f"Processing {file_name}")
    json_path = await clarify(file_name)
    # Move the file to the outputs directory to mark it as processed
    shutil.move(json_path, outputs_directory)
    logger.info(f"Moved {file_name} to {outputs_directory}")
    files_in_process.remove(get_file_name(file_name))
    processed_files.add(get_file_name(file_name))


async def explainer():
    while True:
        # Scan the uploads directory for files
        unprocessed_files = scan_directories()
        for file in unprocessed_files:
            await clarify_file(file)
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(explainer())
