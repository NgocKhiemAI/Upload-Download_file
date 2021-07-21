import motor.motor_asyncio
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from bson.objectid import ObjectId
from fastapi.responses import StreamingResponse

app = FastAPI()



MONGO_DETAILS = "mongodb://ngockhiem:1234@mongodb_container_1:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client["storage"]        # khai bao database
col1 =db["savefile"]      # khai bao col1lection
col2 = db["fs.files"]

fs=motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)



def file_helper(savefile) -> dict:
    return {
        "id": str(savefile["_id"]),
        "Name": savefile["name"],
        "file_id": str(savefile["file_id"]),
        
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

async def add(file_data: dict) -> dict:
    file_id = await fs.upload_from_stream(
        file_data.filename,
        await file_data.read(),
        metadata={"contentType": "text/plain"})

    id=await col1.insert_one({"name":file_data.filename,"file_id":file_id})
    return str(id.inserted_id)

# upload file using gridfs
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    content = await add(file) 
    return content

@app.put("/document/")
async def open_document_contain_file(id: str) -> dict :
    savefile = await col1.find_one({"_id": ObjectId(id)})
    if savefile:
        return file_helper(savefile)

#get information of uploaded file
@app.put("/information/")
async def information_file(file_id: str) -> dict :
    files = await col2.find_one({"_id": ObjectId(file_id)})
    if files:
        return fs_helper(files)

# open_download_stream up to stream
async def download_stream(file_id):
    # get _id of file to read.
    File_id = ObjectId(file_id)
    grid_out = await fs.open_download_stream(File_id)
    contents = await grid_out.read()
    yield contents

# read content of file 
@app.put("/content/")
async def download_file(file_id: str) -> dict :
    return StreamingResponse(download_stream(file_id), media_type="text/plain")
