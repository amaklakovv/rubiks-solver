from fastapi import FastAPI, File, UploadFile
import shutil

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello backend"}

@app.post("/uploadfile/")
async def upload_image(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}