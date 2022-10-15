import os
from fastapi import FastAPI, HTTPException, File, Request, UploadFile
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from pydantic import BaseModel
import sys
from gcp_helpers import upload_blob
from sound_mapper_helpers import textToSound, addSoundToImage
from data import IMAGE_DOWNLOAD_PATH, GCP_BUCKET_NAME, TEMP_FILES_PATH, COMBINED_SOUND_FILENAME, \
    COMBINED_IMAGESOUND_FILENAME

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class UploadConfirmation(BaseModel):
    filename: str
    contenttype: str


@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/", response_model=UploadConfirmation)
async def upload(file: UploadFile = File(...)):
    if not os.path.isdir(IMAGE_DOWNLOAD_PATH):
        os.mkdir(IMAGE_DOWNLOAD_PATH)
    try:
        contents = await file.read()
        input_img_path = IMAGE_DOWNLOAD_PATH + os.sep + file.filename
        with open(input_img_path, 'wb') as f:
            f.write(contents)
        
    except Exception:
        e = sys.exc_info()[1]
        raise HTTPException(status_code=500, detail=str(e))

    # IMG2TXT

    # Tokenizer
    textArray = ["dog", "wind", "train"]

    # TXT2SOUND AND SOUNDSYNTH
    sound = textToSound(textArray)


    # COMBINE IMAGE+SOUND
    addSoundToImage(input_img_path, os.path.join(TEMP_FILES_PATH,COMBINED_SOUND_FILENAME),
                    os.path.join(TEMP_FILES_PATH,COMBINED_IMAGESOUND_FILENAME))

    upload_blob(GCP_BUCKET_NAME, os.path.join(TEMP_FILES_PATH,COMBINED_IMAGESOUND_FILENAME))
    # RETURN VIDEO REQUEST
    return {"filename": file.filename, "contenttype": file.content_type}