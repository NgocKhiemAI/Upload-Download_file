from fastapi import FastAPI,Body
import motor.motor_asyncio 
import uvicorn
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel 
from bson.objectid import ObjectId
import base64


MONGO_DETAILS = "mongodb://ngockhiem:1234@mongodb_container_1:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client['storage']
col = db['savefile']

app =FastAPI()

class input(BaseModel):
    base64: str 
    name : str

def file_helper(savefile) -> dict:
    return {
        "id": str(savefile["_id"]),
        "Name": savefile["name"],
        "content": savefile["base64"]
    }
def export(savefile) -> dict:
    tmp = str(savefile["base64"])
    imgdata = base64.b64decode(tmp)
  

    filename = str(savefile["name"])

    with open(filename, 'wb') as f:
         f.write(imgdata)
    return filename


async def add(file_data: dict) -> dict:

    savefile = await col.insert_one(file_data)
    new_file = await col.find_one({"_id": savefile.inserted_id})
    return file_helper(new_file)

@app.post("/upload/")
async def create_upload(item: input =Body(...) ):
    temp = jsonable_encoder(item)
    content = await add(temp) 
    return content

@app.put("/id")
async def retrieve_image_id(id: str) -> dict:
    savefile = await col.find_one({"_id": ObjectId(id)})
    if savefile:
      return export(savefile)



