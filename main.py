from fastapi import FastAPI,Depends,HTTPException,Form,UploadFile,File
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from server.database.connection import Base,engine,SessionLocal
from server.database.schemas import BinaryImage,DataList



Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

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
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()



@app.get('/',response_class=HTMLResponse)
async def get_home(request:Request,db:Session=Depends(get_db)):

    datas = db.query(DataList).all()
    print(len(datas))

    return templates.TemplateResponse('home.html',{"request":request,"datas":datas})

@app.get('/adddata')
async def get_home(request:Request, db:Session=Depends(get_db)):
    return templates.TemplateResponse('adddata.html',{"request":request})

@app.post('/adddata')
async def add_data(request:Request,db:Session=Depends(get_db),
                   title:str = Form(...), file:UploadFile = File(...)):
    try:

        file_content = await file.read()
        joinfileloc = os.path.join(fileloc,file.filename)
        with open(joinfileloc, "wb") as f:
            f.write(file_content)
        new_data = DataList(id=id,title= title, favorite= file.filename)
        db.add(new_data)

        new_img = BinaryImage(id = id,filename=file.filename, mimetype=file.content_type, content=file_content)
        db.add(new_img)

        instfilter = db.query(DataList).filter(DataList.id == BinaryImage.id).first()

        db.commit()
        db.refresh(instfilter) #session 인스턴스에 대한 refresh는 인스턴스를 주기

        return templates.TemplateResponse('home.html',{"request":request})
    

    except IntegrityError as e:
        db.rollback()
        return {"errorlog: ":e}
    
    finally:
        db.close()
