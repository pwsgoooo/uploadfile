from fastapi import FastAPI,Depends,HTTPException,Form,UploadFile,File
from fastapi.requests import Request
from fastapi.responses import HTMLResponse,JSONResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import os
from PIL import Image
from io import BytesIO
import base64
import builtins
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from server.database.connection import Base,engine,SessionLocal
from server.database.schemas import BinaryImage
from pydantic import BaseModel
from typing import Optional



# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount('/client',StaticFiles(directory=str(Path(__file__).parent.absolute()/'client')), name='client')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

templates = Jinja2Templates(directory='client')


uploadfiles = '/uploadfiles'
if not os.path.exists(uploadfiles):
    os.makedirs(uploadfiles)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def save_img_to_file(id: int, file_fath : str, db:Session=Depends(get_db)):
#     img = db.query(BinaryImage).filter(BinaryImage.id == id).first()

#     if img is None:
#         raise ValueError('Img not found')
    
#     with open (file_fath,'wb') as f:
#         f.write(img.content)


@app.get('/',response_class=HTMLResponse)
async def get_home(request:Request,db:Session=Depends(get_db)):

    datas = db.query(BinaryImage).all()
    print(len(datas))

    return templates.TemplateResponse('home.html',{"request":request,"datas":datas})

@app.get('/adddata')
async def get_home(request:Request, db:Session=Depends(get_db)):
    return templates.TemplateResponse('adddata.html',{"request":request,"db":db})


@app.post("/adddata")
async def add_data(id:int=Form(...), title:str=Form(...), file:UploadFile=File(...), db:Session=Depends(get_db)):
    img = await file.read()

    buf = BytesIO(img)
    # imgview = Image.open(buf)

    buf.seek(0)
    bdata = buf.getvalue()

    # 파일로 저장은 작동안함
    # joinuploadfiles = os.path.join(uploadfiles,file.filename)
    # with open(joinuploadfiles, 'wb') as f:
    #     f.write(bdata)

    result = base64.b64decode(bdata)

    form_data = {"id": id, "title": title, "file": file}
    
    new_d = BinaryImage(id = id,title = title,filename = file.filename, content=result)
    db.add(new_d)
    print("datalist update finished")
    db.commit()
    db.refresh(new_d)

    return form_data

@app.get("/imageview/{image_id}",response_class=HTMLResponse)
async def get_image(request:Request, image_id: int, db: Session = Depends(get_db)):
    img = db.query(BinaryImage).filter(BinaryImage.id == image_id).first()


    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return templates.TemplateResponse('imgview.html',{"request":request,"db":db,"image_id": image_id})




def create_image_with_binary_data(binary_data: bytes) -> Image:
    # 바이너리 데이터를 BytesIO 객체로 변환
    buffer = BytesIO(binary_data)
    
    # BytesIO 객체를 사용하여 이미지 열기
    image = Image.open(buffer)
    
    return image

@app.get("/imageview/{image_id}/stream",response_class=StreamingResponse)
async def get_image(request:Request, image_id: int,  db: Session = Depends(get_db)):
    img = db.query(BinaryImage).filter(BinaryImage.id == image_id).first()
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")

    if not isinstance(img.content, bytes):
        raise HTTPException(status_code=500, detail="Invalid image data format")
    

    

    blob_data = img.content
    # imgobj = Image.open(buf)

    print("blob_data:",blob_data)

    # b_data = base64.b64encode(blob_data).decode('utf-8')
    buf = BytesIO(blob_data)
    
    buf.seek(0)

    print("buf:",buf)



    return StreamingResponse (buf,media_type='image/jpeg',headers={"Content-Disposition": f"inline; filename={img.filename}"})