from fastapi import FastAPI, File, UploadFile
import uvicorn
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    friend = jsonable_encoder(contents)
    return JSONResponse(content=friend)