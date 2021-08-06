from typing import List
import motor.motor_asyncio
from fastapi import FastAPI, File, UploadFile, Depends
import uvicorn
from bson.objectid import ObjectId
from fastapi.responses import StreamingResponse
import hashlib

app = FastAPI()

MONGO_DETAILS = "mongodb://ngockhiem:1234@mongodb_containers:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client["Database"]        # khai bao database
col1 = db["Image"]      # khai bao col1lection
col2 = db["fs.files"]

fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)


def file_helper(Image) -> dict:
    return {
        "id": str(Image ["_id"]),
        "Name": Image ["name"],
        "file_id": str(Image ["file_id"]),
        
    }

def fs_helper(files) -> dict:
    return {
        "Name": files["filename"],
        "md5": files["md5"],
        "length": files["length"],
        "chunkSize":files["chunkSize"],
        "uploadDate": files["uploadDate"],
        "metadata": files["metadata"],
    }



 # function for add data

async def add(file_data: dict,data: bytes) -> dict:
    file_id = await fs.upload_from_stream(
        file_data.filename,
        data,
        metadata={"contentType": "text/plain"})
    id = await col1.insert_one({"name":file_data.filename,"file_id":file_id})
    return  str(id.inserted_id)


# upload 1 file using gridfs

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    data = await file.read()
    hash_obj = hashlib.md5(data)
    md5_file = hash_obj.hexdigest()
    if (tmp := await db.fs.files.find_one({"md5": md5_file})) is not None:
        return {str(tmp["_id"])}
    else:
        content = await add(file,data)
        return {"ID": content}


# upload multiple file

@app.post("/upload-multiple-file/")
async def upload_multiple(files: List[UploadFile] = File(...)):
    lst = []
    for i in files:
        data = await i.read()
        hash_obj = hashlib.md5(data)
        md5_file = hash_obj.hexdigest()
        
        if (tmp := await db.fs.files.find_one({"md5": md5_file})) is not None:
            lst.append(str(tmp["_id"]))
        else:
            temp = await add(i,data) 
            lst.append(temp)
    return {"ID": lst }



# open collection to get id
@app.put("/get-file-id/")
async def open_col(ID: str ) -> dict :
    if len(ID) == 24 :
        if (contain := await col1.find_one({"_id": ObjectId(ID)})) is not None :
            return file_helper(contain)
        else:
            return {"Error": "ID does not exist" }
    else:
        return {"Error": "ID length must be 24 characters" }

    

#open fs.files to get information of uploaded file
@app.put("/information/")
async def information_file(file_id: str) -> dict :
    if len(file_id) == 24 :
        if (file := await col2.find_one({"_id": ObjectId(file_id)})) is not None :
            return fs_helper(file)
        else:
            return {"Error": "file_id does not exist" }
    else:
        return {"Error": "file_id length must be 24 characters" }

# open_download_stream up to stream
async def download_stream(file_id):

    File_id = ObjectId(file_id)
    grid_out = await fs.open_download_stream(File_id)
    contents = await grid_out.read()   
    yield contents

# read image
@app.put("/read-image/")
async def download_file(file_id: str) -> dict :
    if len(file_id) == 24 :
        if (file := await col2.find_one({"_id": ObjectId(file_id)})) is not None :
            return StreamingResponse(download_stream(file_id), media_type="image/png")
        else:
            return {"Error": "file_id does not exist" }
    else:
        return {"Error": "file_id length must be 24 characters" }    



