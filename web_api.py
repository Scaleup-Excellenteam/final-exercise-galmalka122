import os
from datetime import datetime
from glob import glob
from uuid import uuid4
from dotenv import load_dotenv
from flask import Flask, request, make_response, jsonify

load_dotenv()

app = Flask(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR") or "uploads"
OUTPUT_DIR = os.getenv("OUTPUT_DIR") or "outputs"


def process_file(uploaded_file):
    """
    Process the uploaded file and save it to the uploads folder.
    Args:
        uploaded_file: The uploaded file.

    Returns:
        The UUID of the uploaded file.
    """

    # Get the original file name and file extension
    file_name, file_extension = os.path.splitext(uploaded_file.filename)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Generate UUID
    file_uuid = str(uuid4())

    # Create new file name
    new_file_name = f"{UPLOAD_DIR}/{file_name}_{timestamp}_{file_uuid}{file_extension}"

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

    uploaded_file = request.files['the_file']
    file_uuid = process_file(uploaded_file)
    return {"file_uuid": file_uuid,
            "message": "file uploaded successfully"}


@app.get('/upload')
def upload_file():
    return "<form action=\"\" method=\"post\" enctype=\"multipart/form-data\">" \
           "<input type=\"file\" name=\"the_file\" />" \
           "<input type=\"submit\" value=\"Upload\" />" \
           "</form>"


@app.get('/status')
def get_status():
    file_uuid = request.args.get('uuid')
    pattern = f"{UPLOAD_DIR}/*{file_uuid}*"
    matching_files = glob(pattern)
    if len(matching_files) == 0:
        response = make_response({"status": "not found"}, 404)
    else:
        _, matching_file_name = os.path.split(matching_files[0])
        file_name, timestamp, _ = matching_file_name.split("_")
        path = f"{OUTPUT_DIR}/{file_name}_{timestamp}_{file_uuid}.json"
        response_body = {
            "filename": file_name,
            "timestamp": timestamp,
            "explanation": None,
            "status": "pending"
        }
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
