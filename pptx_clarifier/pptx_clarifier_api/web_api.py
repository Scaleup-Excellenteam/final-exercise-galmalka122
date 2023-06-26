import os
import threading
from datetime import datetime
from glob import glob
from uuid import uuid4
from dotenv import load_dotenv
from flask import Flask, request, make_response, jsonify

from ..definitions import uploads_directory, outputs_directory
from pptx_clarifier.pptx_clarifier_api import api_logger as logger

load_dotenv()

app = Flask(__name__)


def process_file(uploaded_file):
    """
    Process the uploaded file and save it to the uploads folder.
    Args:
        uploaded_file: The original file name.

    Returns:
        The UUID of the uploaded file.
    """

    # Get the original file name and file extension
    file_name, file_extension = os.path.splitext(uploaded_file.filename)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Generate UUID
    file_uuid = str(uuid4().hex)

    # Create new file name
    new_file_name = os.path.join(uploads_directory, f"{file_name}_{timestamp}_{file_uuid}{file_extension}")

    # Save the uploaded file with the new name
    uploaded_file.save(new_file_name)

    return file_uuid


@app.post('/upload')
def save_file():
    """
    Upload a file to the server.

    Returns:
        A JSON object containing the UUID of the uploaded file.
    """

    uploaded_file = request.files['file']
    file_uuid = process_file(uploaded_file)
    logger.info(f"file uploaded with uid: {file_uuid}")
    return make_response({"file_uuid": file_uuid, "message": "file uploaded successfully"}, 200)


@app.get('/upload')
def upload_file():
    return "<form action=\"\" method=\"post\" enctype=\"multipart/form-data\">" \
           "<input type=\"file\" name=\"file\" />" \
           "<input type=\"submit\" value=\"Upload\" />" \
           "</form>"


@app.get('/status')
def get_status():
    """
    Get the status of the uploaded file. If the file is processed, return the explanation.

    Returns:
        A JSON object containing the status of the uploaded file.
    """

    # Get the UUID of the uploaded file from the query string
    file_uuid = request.args.get('uuid')

    # Find the file in the uploads folder using the UUID as a pattern
    pattern = f"{uploads_directory}/*{file_uuid}*"
    matching_files = glob(pattern)

    # If the file is not found, return 404
    if len(matching_files) == 0:
        response = make_response({"status": "not found"}, 404)
    else:
        # Get the file name and timestamp from the first matching and search for the file in the outputs folder
        _, matching_file_name = os.path.split(matching_files[0])
        file_name, timestamp, _ = matching_file_name.split("_")
        path = os.path.join(outputs_directory, f"{file_name}_{timestamp}_{file_uuid}.json")

        # initialize the response body
        response_body = {
            "filename": file_name,
            "timestamp": timestamp,
            "explanation": None,
            "status": "pending"
        }
        # If the file is found, return the explanation and status 200. Otherwise, return status 202
        if os.path.exists(path):
            with open(path, "r") as f:
                data = f.read()
                response_body["explanation"] = data
                response_body["status"] = "done"
            response = make_response(jsonify(response_body), 200)
        else:
            response = make_response(jsonify(response_body), 202)

    return response


if __name__ == "__main__":
    app.run()
