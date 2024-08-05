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


fileloc = '/fileloc'
if not os.path.exists(fileloc):
    os.makedirs(fileloc)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_img_to_file(id: int, file_fath : str, db:Session=Depends(get_db)):
    img = db.query(BinaryImage).filter(BinaryImage.id == id).first()

    if img is None:
        raise ValueError('Img not found')
    
    with open (file_fath,'wb') as f:
        f.write(img.content)


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


    joinfileloc = os.path.join(fileloc,file.filename)
    with open(joinfileloc, 'wb') as f:
        f.write(bdata)

    result = base64.b64decode(bdata)

    form_data = {"id": id, "title": f, "file": file}
    
    new_d = BinaryImage(id = id,title = title,filename = file.filename, content=result)
    db.add(new_d)
    print("datalist update finished")


    db.commit()
    db.refresh(new_d)

    return form_data

@app.get("/{image_id}",response_class=HTMLResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    img = db.query(BinaryImage).filter(BinaryImage.id == image_id).first()
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 이미지 바이너리 데이터를 StreamingResponse로 반환
    return StreamingResponse(BytesIO(img.content), media_type='image/png', headers={"Content-Disposition": f"inline; filename={img.filename}"})


@app.get("/", response_class=HTMLResponse)
async def read_root(db:Session=Depends(get_db)):

    ids = db.query(BinaryImage).all()
    image_ids = []
    for image_id in len(ids):
        image_ids.append(image_id['id'])

    print(image_ids)

    html_content = "<html><body><h1>Image Gallery</h1>"
    for image_id in image_ids:
        html_content += f'<p><img src="/"/{image_id}" alt="Image {image_id}" style="max-width: 100%; height: auto;"></p>'
    html_content += "</body></html>"
    
    return HTMLResponse(content=html_content)
